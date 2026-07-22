"""Deterministic scheme eligibility engine."""

from typing import Any

from app.models.schemas import EligibilityProfile, EligibilityResponse, SchemeDecision
from app.utils.json_loader import load_schemes
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EligibilityEngine:
    """Evaluate eligibility_rules in schemes.json without AI."""

    FLAG_ALIASES: dict[str, tuple[str, ...]] = {
        "is_ap_resident": ("is_ap_resident", "ap_resident"),
        "has_rice_card": ("has_rice_card", "rice_card", "has_ration_card"),
        "has_ration_card": ("has_ration_card", "ration_card", "has_rice_card"),
        "is_farmer": ("is_farmer", "farmer"),
        "has_cultivable_land": ("has_cultivable_land", "farmer"),
        "has_valid_land_records": ("has_valid_land_records", "has_digitized_land_records"),
        "has_digitized_land_records": ("has_digitized_land_records", "has_valid_land_records"),
        "owns_four_wheeler": ("owns_four_wheeler", "four_wheeler"),
        "electricity_above_300_units": ("electricity_above_300_units",),
        "wetland_above_3_acres": ("wetland_above_3_acres",),
        "disabled": ("disabled", "is_disabled"),
        "widow": ("widow", "is_widow"),
        "is_student": ("is_student", "student"),
        "has_child_in_school": ("has_child_in_school", "student"),
        "studying_in_college": ("studying_in_college", "student"),
        "aadhaar_linked_to_bank": ("aadhaar_linked_to_bank", "aadhaar_linked", "bank_aadhaar_linked"),
        "has_active_bank_account": ("has_active_bank_account", "bank_account_active"),
    }

    CATEGORY_FLAGS: dict[str, tuple[str, ...]] = {
        "senior_65_plus": ("senior_65_plus", "age_65_plus"),
        "widow": ("widow", "is_widow"),
        "disabled": ("disabled", "is_disabled"),
        "student": ("student", "is_student"),
    }

    def evaluate(self, profile: EligibilityProfile) -> EligibilityResponse:
        """Classify every scheme as eligible, needs more information, or not eligible."""

        answers = self._flatten_profile(profile)
        eligible: list[SchemeDecision] = []
        need_more_information: list[SchemeDecision] = []
        not_eligible: list[SchemeDecision] = []

        for scheme in load_schemes().values():
            decision = self._evaluate_scheme(scheme, answers, profile)
            if decision.status == "eligible":
                eligible.append(decision)
            elif decision.status == "need_more_information":
                need_more_information.append(decision)
            else:
                not_eligible.append(decision)

        logger.info(
            "Eligibility evaluated: eligible=%s need_more_information=%s not_eligible=%s",
            len(eligible),
            len(need_more_information),
            len(not_eligible),
        )
        return EligibilityResponse(
            eligible=eligible,
            need_more_information=need_more_information,
            not_eligible=not_eligible,
        )

    def _flatten_profile(self, profile: EligibilityProfile) -> dict[str, Any]:
        answers = dict(profile.answers)
        derived = {
            "district": profile.district,
            "income": profile.income,
            "annual_income": profile.annual_income,
            "location": profile.location,
            "has_rice_card": profile.has_rice_card,
            "has_ration_card": profile.has_ration_card,
            "farmer": profile.farmer,
            "disabled": profile.disabled,
            "widow": profile.widow,
            "student": profile.student,
            "electricity_units": profile.electricity_units,
            "land": profile.land,
            "four_wheeler": profile.four_wheeler,
        }
        answers.update({key: value for key, value in derived.items() if value is not None})
        if profile.district:
            answers.setdefault("is_ap_resident", True)
        if profile.electricity_units is not None:
            answers["electricity_above_300_units"] = profile.electricity_units > 300
        if profile.land is not None:
            answers["wetland_above_3_acres"] = profile.land > 3
        return answers

    def _evaluate_scheme(
        self,
        scheme: dict[str, Any],
        answers: dict[str, Any],
        profile: EligibilityProfile,
    ) -> SchemeDecision:
        rules = scheme.get("eligibility_rules", {})
        reasons: list[str] = []
        missing_info: list[str] = []
        missing_flags: list[str] = []
        failed = False

        residence = str(rules.get("residence", "")).lower()
        if "andhra pradesh" in residence and not self._truthy(answers, "is_ap_resident"):
            if profile.district:
                reasons.append("Applicant appears to be in Andhra Pradesh based on district.")
            else:
                missing_info.append("Andhra Pradesh residence or district")
                missing_flags.append("is_ap_resident")

        for flag in rules.get("required_flags", []):
            value = self._lookup_flag(answers, flag)
            if value is None:
                missing_info.append(self._humanize(flag))
                missing_flags.append(flag)
            elif not bool(value):
                failed = True
                reasons.append(f"Required condition not met: {self._humanize(flag)}.")

        for flag in rules.get("exclusions", []):
            value = self._lookup_flag(answers, flag)
            if value is True:
                failed = True
                reasons.append(f"Excluded because {self._humanize(flag)} applies.")

        failed |= not self._check_income(rules, answers, reasons, missing_info, missing_flags)
        failed |= not self._check_categories(rules, answers, reasons, missing_info, missing_flags)

        if failed:
            status = "not_eligible"
        elif missing_info:
            status = "need_more_information"
            reasons.append("No exclusion matched; more information is needed before confirming eligibility.")
        else:
            status = "eligible"
            reasons.append("All mandatory eligibility rules are satisfied from the supplied information.")

        unique_missing_flags = self._prioritize_missing_flags(self._unique(missing_flags), answers)
        return SchemeDecision(
            scheme_id=scheme.get("id", ""),
            scheme_name=scheme.get("name", ""),
            category=scheme.get("category"),
            status=status,
            eligible=status == "eligible",
            reasons=reasons,
            missing_information=self._unique(missing_info),
            missing_questions=[self._question_for(flag) for flag in unique_missing_flags],
            next_questions=[self._question_for(flag) for flag in unique_missing_flags[:2]],
            missing_documents=scheme.get("documents", []),
            benefits=self._benefits(scheme),
            application_links=[scheme["portal"]] if scheme.get("portal") else [],
            processing_time=scheme.get("processing_time"),
            confidence=self._confidence(rules, unique_missing_flags, failed),
        )

    def _check_income(
        self,
        rules: dict[str, Any],
        answers: dict[str, Any],
        reasons: list[str],
        missing_info: list[str],
        missing_flags: list[str],
    ) -> bool:
        income_check = rules.get("income_check")
        if isinstance(income_check, dict):
            location = str(answers.get("location", "")).lower()
            income = answers.get("income")
            if income is None:
                missing_info.append("monthly income")
                missing_flags.append("income")
                return True
            limit = income_check.get("urban_max_monthly") if location == "urban" else income_check.get("rural_max_monthly")
            if limit is not None and float(income) > float(limit):
                reasons.append(f"Monthly income exceeds the {location or 'rural'} limit of {limit}.")
                return False

        annual_bands = rules.get("income_bands_annual")
        if isinstance(annual_bands, dict):
            annual_income = answers.get("annual_income")
            if annual_income is None and answers.get("income") is not None:
                annual_income = float(answers["income"]) * 12
            if annual_income is None:
                missing_info.append("annual income")
                missing_flags.append("annual_income")
                return True
            max_limit = max(float(value) for value in annual_bands.values())
            if float(annual_income) > max_limit:
                reasons.append(f"Annual income exceeds the maximum listed band of {max_limit}.")
                return False

        return True

    def _check_categories(
        self,
        rules: dict[str, Any],
        answers: dict[str, Any],
        reasons: list[str],
        missing_info: list[str],
        missing_flags: list[str],
    ) -> bool:
        categories = rules.get("categories")
        if not isinstance(categories, list):
            return True

        matched = False
        known = False
        for category in categories:
            aliases = self.CATEGORY_FLAGS.get(category, (category,))
            values = [answers.get(alias) for alias in aliases if alias in answers]
            known = known or bool(values)
            matched = matched or any(bool(value) for value in values)

        if matched:
            return True
        if known:
            reasons.append("Applicant does not match any listed beneficiary category.")
            return False
        missing_info.append("eligible beneficiary category")
        missing_flags.append("belongs_to_eligible_category")
        return True

    def _lookup_flag(self, answers: dict[str, Any], flag: str) -> Any:
        for alias in self.FLAG_ALIASES.get(flag, (flag,)):
            if alias in answers:
                return answers[alias]
        return None

    def _truthy(self, answers: dict[str, Any], flag: str) -> bool:
        return bool(self._lookup_flag(answers, flag))

    def _benefits(self, scheme: dict[str, Any]) -> list[str]:
        benefits = []
        if scheme.get("benefit"):
            benefits.append(scheme["benefit"])
        breakdown = scheme.get("benefit_breakdown")
        if isinstance(breakdown, dict):
            benefits.extend(f"{key}: {value}" for key, value in breakdown.items())
        return benefits

    def _confidence(self, rules: dict[str, Any], missing_flags: list[str], failed: bool) -> float:
        if failed:
            return 1.0
        required_count = len(rules.get("required_flags", []))
        required_count += 1 if rules.get("income_check") else 0
        required_count += 1 if rules.get("income_bands_annual") else 0
        required_count += 1 if rules.get("categories") else 0
        if required_count == 0:
            return 1.0
        answered = max(0, required_count - len(set(missing_flags)))
        return round(answered / required_count, 2)

    def _question_for(self, flag: str) -> str:
        question_map = {
            "is_ap_resident": "Are you a resident of Andhra Pradesh?",
            "has_rice_card": "Do you have a rice card or ration card?",
            "has_ration_card": "Do you have a rice card or ration card?",
            "is_farmer": "Are you a farmer?",
            "has_digitized_land_records": "Do you have digitized land records such as Webland, Adangal, or 1B?",
            "has_valid_land_records": "Do you have valid land ownership or cultivation records?",
            "aadhaar_linked": "Is your Aadhaar linked for this application?",
            "aadhaar_linked_to_bank": "Is Aadhaar linked with your bank account for DBT?",
            "ekyc_done": "Have you completed eKYC?",
            "has_active_bank_account": "Do you have an active NPCI-mapped bank account?",
            "has_child_in_school": "Do you have a child currently studying in school?",
            "child_attendance_above_75": "Was the child's attendance above 75 percent in the previous academic year?",
            "belongs_to_eligible_category": "Do you belong to one of the eligible beneficiary categories for this scheme?",
            "income": "What is your monthly household income?",
            "annual_income": "What is your annual household income?",
        }
        return question_map.get(flag, f"Can you confirm: {self._humanize(flag)}?")

    def _humanize(self, flag: str) -> str:
        return flag.replace("_", " ")

    def _unique(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        unique_values = []
        for value in values:
            if value not in seen:
                seen.add(value)
                unique_values.append(value)
        return unique_values

    def _prioritize_missing_flags(self, flags: list[str], answers: dict[str, Any]) -> list[str]:
        priority = [
            "has_digitized_land_records",
            "has_valid_land_records",
            "ekyc_done",
            "aadhaar_linked_to_bank",
            "has_active_bank_account",
            "has_child_in_school",
            "child_attendance_above_75",
            "income",
            "annual_income",
            "has_rice_card",
            "has_ration_card",
            "belongs_to_eligible_category",
            "is_ap_resident",
        ]
        if not bool(answers.get("farmer")):
            priority = [flag for flag in priority if "land_records" not in flag and flag != "ekyc_done"]
        return sorted(flags, key=lambda flag: priority.index(flag) if flag in priority else len(priority))

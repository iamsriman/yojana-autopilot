import { AnimatePresence, motion } from "framer-motion";
import { useRoute } from "./router";

export default function App() {
  const { Component, path } = useRoute();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={path}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.18 }}
      >
        <Component />
      </motion.div>
    </AnimatePresence>
  );
}

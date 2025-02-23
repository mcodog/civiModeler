import React, { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  scaleAnimation,
  containerAnimation,
  slideUpAnimation,
  fadeInAnimation,
} from "../Anims/Simple";
import PrimeBtn from "../Components/PrimeBtn";
import loader from "../assets/loaders/build.gif";
import ModelViewer from "../Utils/ModelViewer";

const questions = [
  { id: "budget", label: "What's your budget like?", placeholder: "$0.00" },
  {
    id: "width",
    label: "What’s the location width?",
    placeholder: "5 square feet",
  },
  {
    id: "length",
    label: "What’s the location length?",
    placeholder: "5 square feet",
  },
];

const loadingMessages = [
  "Shaping the blueprint...",
  "Hearing the walls whisper...",
  "Finding the right angle...",
  "Bringing together the pieces...",
  "Tuning the foundations...",
  "Smoothing out the edges...",
  "Aligning the beams of creativity...",
  "Whistling through the scaffolding...",
  "Building a bridge to somewhere...",
  "Filling the empty spaces...",
];

const Welcome = () => {
  const [Status, setStatus] = useState("Start");
  const [params, setParams] = useState({ budget: "", width: "", length: "" });
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState(loadingMessages[0]);

  useEffect(() => {
    const interval = setInterval(() => {
      setLoadingText((prev) => {
        const currentIndex = loadingMessages.indexOf(prev);
        const nextIndex = (currentIndex + 1) % loadingMessages.length;
        return loadingMessages[nextIndex];
      });
    }, 800);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (Status == "Finished") {
      setTimeout(() => {
        setLoading(false);
      }, 5000);
    }
  }, [Status]);

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
    } else {
      setLoading(true);
      setStatus("Finished");
      console.log("Final Params:", params);
    }
  };

  return (
    <motion.div
      layout
      className="min-h-screen w-full flex flex-col justify-center items-center bg-gray-200 overflow-hidden"
    >
      {Status == "Finished" && (
        <ModelViewer loading={loading} params={params} />
      )}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={scaleAnimation.initial}
            animate={scaleAnimation.animate}
            className="flex flex-col justify-center items-center absolute top-0 left-0 w-full h-full"
          >
            <motion.div className="h-52 w-52 bg-white flex justify-center items-center rounded-full custom-shadow">
              <img src={loader} className="h-full w-full rounded-full" />
            </motion.div>
            <div className="w-full text-center my-16 text-2xl font-comfortaa">
              {loadingText}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      <AnimatePresence mode="popLayout">
        {Status == "Start" && (
          <motion.div
            variants={containerAnimation}
            initial="initial"
            animate="animate"
            exit={{ opacity: 0, scale: 0 }}
            className="flex flex-col items-center"
          >
            <motion.div
              variants={scaleAnimation.variants}
              transition={scaleAnimation.transition}
            >
              <div className="font-comfortaa text-4xl text-center">Welcome</div>
              <div className="font-comfortaa text-xl text-gray-500 text-center">
                Click on the button below to get Statused
              </div>
            </motion.div>
            <motion.div
              variants={scaleAnimation.variants}
              transition={scaleAnimation.transition}
              className="my-8 p-2"
            >
              <PrimeBtn onClick={() => setStatus("Query")} text="Let's Begin" />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence mode="popLayout">
        {Status == "Query" && (
          <motion.div
            key={questions[currentQuestion].id}
            variants={containerAnimation}
            initial="initial"
            animate="animate"
            exit={slideUpAnimation.exit}
            className="flex flex-col justify-center items-center gap-10"
            layout
          >
            <motion.div
              variants={slideUpAnimation.variants}
              transition={slideUpAnimation.transition}
              className="font-comfortaa text-2xl"
            >
              {questions[currentQuestion].label}
            </motion.div>

            <motion.div
              variants={slideUpAnimation.variants}
              transition={slideUpAnimation.transition}
              className="flex flex-col gap-5"
            >
              <input
                placeholder={questions[currentQuestion].placeholder}
                type="text"
                value={params[questions[currentQuestion].id]}
                onChange={(e) =>
                  setParams({
                    ...params,
                    [questions[currentQuestion].id]: e.target.value,
                  })
                }
                className="font-comfortaa border-1 h-20 p-1 px-4 rounded-2xl bg-gray-300 custom-text__input"
              />
              <AnimatePresence mode="popLayout">
                {params[questions[currentQuestion].id].length !== 0 && (
                  <motion.div
                    initial={fadeInAnimation.initial}
                    animate={fadeInAnimation.animate}
                    className="w-full"
                  >
                    <PrimeBtn
                      text={
                        currentQuestion === questions.length - 1
                          ? "Finish"
                          : "Next"
                      }
                      onClick={handleNext}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default Welcome;

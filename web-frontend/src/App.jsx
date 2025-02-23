import React from "react";
import { Route, Routes } from "react-router-dom";
import "./App.css";

import Welcome from "./Pages/Welcome";
import { Provider } from "react-redux";
import store from "./Redux/store";

const App = () => {
  return (
    <Provider store={store}>
      <Routes>
        <Route index element={<Welcome />} />
      </Routes>
    </Provider>
  );
};

export default App;

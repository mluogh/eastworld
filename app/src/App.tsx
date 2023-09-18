import "./App.scss";
import { Box, ChakraProvider, Center } from "@chakra-ui/react";
import theme from "./theme";

// import { BrowserRouter as Router, Route } from "react-router-dom";
import { Route, Routes } from "react-router-dom";

import GameList from "components/GameList";
import Navbar from "components/Navbar";
import { OpenAPI } from "client";
import Game from "components/Game";
import Agent from "components/Agent";

function App() {
  OpenAPI.BASE = "/api";

  return (
    <ChakraProvider theme={theme}>
      <Center>
        <Navbar></Navbar>
      </Center>
      <Center>
        <Box width={{ lg: "800px", xl: "1100px" }}>
          <Routes>
            <Route path="/" element={<GameList />}></Route>
            <Route path="/game/:gameUuid" element={<Game />}></Route>
            <Route
              path="/game/:gameUuid/agent/:agentUuid"
              element={<Agent />}
            ></Route>
            <Route path="*" element={<Box>Not Found</Box>}></Route>
          </Routes>
        </Box>
      </Center>
    </ChakraProvider>
  );
}

export default App;

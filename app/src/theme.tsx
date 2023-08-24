import { extendTheme } from "@chakra-ui/react";

// const breakpoints = {
//   sm: "360px",
//   md: "768px",
//   lg: "1200px",
//   // xl: "1200px",
// };

const theme = extendTheme({
  colors: {
    brand: {
      main: "#333333",
      cream: "#FFFFFF",
    },
    web: {
      body: "#FFFFFF",
    },
  },
  fonts: {
    heading: `'Open Sans', sans-serif`,
    body: `'Raleway', sans-serif`,
  },
  // breakpoints,
});

export default theme;

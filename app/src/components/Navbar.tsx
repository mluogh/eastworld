import { Box, Flex, Heading } from "@chakra-ui/react";

export default function Navbar() {
  return (
    <Box bg={"brand.cream"} px={10}>
      <Flex h={16} alignItems={"center"} justifyContent={"space-between"}>
        <Heading size={"lg"} color={"brand.main"}>
          eastworld Agents
        </Heading>
      </Flex>
    </Box>
  );
}

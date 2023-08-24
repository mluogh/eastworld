import {
  Card,
  Text,
  CardHeader,
  CardBody,
  Heading,
  Center,
  Grid,
  Flex,
} from "@chakra-ui/react";
import { AgentDef } from "client";
import { AddIcon } from "@chakra-ui/icons";
import { useParams, useNavigate } from "react-router-dom";

interface AgentListProps {
  agents: AgentDef[];
  addAgent: () => Promise<void>;
}

export default function AgentList(props: AgentListProps) {
  const nav = useNavigate();
  const params = useParams();

  return (
    <>
      <Center>
        <Heading size={"xl"} margin={10}>
          Agents
        </Heading>
      </Center>
      <Grid templateColumns="repeat(2, 1fr)" gap={8} marginBottom={100}>
        <Card onClick={() => props.addAgent()} style={{ cursor: "pointer" }}>
          <Flex flexDirection="column" justify="center" h="100%">
            <CardHeader>
              <Center>
                <Heading size="lg">
                  New Agent
                  <AddIcon marginLeft={3} />
                </Heading>
              </Center>
            </CardHeader>
          </Flex>
        </Card>
        {props.agents.map((agent, index) => (
          <Card
            key={index}
            style={{ cursor: "pointer" }}
            onClick={() => nav(`/game/${params.gameUuid!}/agent/${agent.uuid}`)}
          >
            <CardHeader>
              <Heading size="lg">{agent.name}</Heading>
            </CardHeader>
            <CardBody>
              <Text noOfLines={5} whiteSpace={"pre-wrap"}>
                {agent.description || "No description yet!"}
              </Text>
            </CardBody>
          </Card>
        ))}
      </Grid>
    </>
  );
}

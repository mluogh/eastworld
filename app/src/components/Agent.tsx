import { Box, Button, Grid, HStack, Spacer } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { AgentDef, AgentDefinitionsService, GameSessionsService } from "client";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowBackIcon } from "@chakra-ui/icons";
import AgentEdit from "./AgentEdit";
import AgentChat from "components/AgentChat";
import DeleteModal from "util/DeleteModal";

export default function Agent() {
  const [agent, setAgent] = useState<AgentDef>();

  const params = useParams();
  useEffect(() => {
    const fetchData = async () => {
      setAgent(
        await AgentDefinitionsService.getAgent(
          params.gameUuid!,
          params.agentUuid!,
        ),
      );
    };
    fetchData();
  }, [params]);

  const handleSave = async (def: AgentDef) => {
    setAgent(
      await AgentDefinitionsService.updateAgent(
        params.gameUuid!,
        params.agentUuid!,
        def,
      ),
    );
    await GameSessionsService.syncSessionsToGameDefs(params.gameUuid!);
  };

  const nav = useNavigate();
  let buttons = (
    <>
      <HStack width="full">
        <Button
          leftIcon={<ArrowBackIcon />}
          onClick={() => nav(`/game/${params.gameUuid}`)}
          marginBottom={"20px"}
        >
          Back
        </Button>
        <Spacer />
        <DeleteModal
          text="Are you sure you want to delete this agent?"
          onDelete={async () => {
            await AgentDefinitionsService.deleteAgent(
              params.gameUuid!,
              params.agentUuid!,
            );

            nav(`/game/${params.gameUuid}`);
          }}
        />
      </HStack>
    </>
  );
  if (!agent) {
    return <Box>{buttons}</Box>;
  }

  return (
    <Box>
      {buttons}
      <Grid templateColumns="repeat(2, 1fr)">
        <AgentEdit agent={agent} handleSave={handleSave}></AgentEdit>
        <AgentChat></AgentChat>
      </Grid>
    </Box>
  );
}

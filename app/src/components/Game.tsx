import {
  Box,
  Button,
  VStack,
  Heading,
  Text,
  HStack,
  Spacer,
  Tabs,
  Tab,
  TabPanels,
  TabPanel,
  TabList,
  Center,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import {
  AgentDefinitionsService,
  GameDef,
  GameDefinitionsService,
  GameSessionsService,
} from "client";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowBackIcon } from "@chakra-ui/icons";
import GameEdit, { GameDefSubset } from "./GameEdit";
import AgentList from "./AgentList";
import DeleteModal from "util/DeleteModal";
import GameLore from "./GameLore";
import { Lore } from "client";

export default function Game() {
  const [editingGame, setEditingGame] = useState<boolean>(false);
  const [game, setGame] = useState<GameDef>();

  const params = useParams();
  useEffect(() => {
    const fetchData = async () => {
      setGame(await GameDefinitionsService.getGame(params.gameUuid!));
    };
    fetchData();
  }, [params]);

  const handleSave = async (def: GameDef) => {
    delete def.agents;
    setGame(
      await GameDefinitionsService.updateGame(
        params.gameUuid!,
        def,
        /*overwriteAgents=*/ false,
      ),
    );
    await GameSessionsService.syncSessionsToGameDefs(params.gameUuid!);
    setEditingGame(false);
  };

  const handleSaveDescription = async (def: GameDefSubset) => {
    await handleSave({ ...game, ...def });
  };

  const handleSaveLore = async (lore: Lore[]) => {
    await handleSave({ ...game!, shared_lore: lore });
  };

  const handleCancel = () => {
    setEditingGame(false);
  };

  const handleAddAgent = async () => {
    let agent = await AgentDefinitionsService.createAgent(
      params.gameUuid!,
      "New Agent",
    );
    nav(`agent/${agent.uuid!}`);
  };

  const nav = useNavigate();
  let buttons = (
    <>
      <HStack width="full">
        <Button
          leftIcon={<ArrowBackIcon />}
          onClick={() => nav("/")}
          marginBottom={"20px"}
        >
          Back
        </Button>
        <Spacer />
        <DeleteModal
          text="Are you sure you want to delete this game?"
          onDelete={async () => {
            await GameDefinitionsService.deleteGame(params.gameUuid!);

            nav("/");
          }}
        />
      </HStack>
    </>
  );
  if (!game) {
    return <Box>{buttons}</Box>;
  }

  let gamePanel;

  if (editingGame) {
    gamePanel = (
      <GameEdit
        game={game}
        handleSave={handleSaveDescription}
        handleCancel={handleCancel}
      ></GameEdit>
    );
  } else {
    gamePanel = (
      <VStack spacing={10} align={"center"} marginTop={10}>
        <Heading size={"3xl"}>{game.name}</Heading>
        <Text>{game.description}</Text>
        <Button
          colorScheme="purple"
          onClick={() => setEditingGame(true)}
          width={"50%"}
        >
          Edit
        </Button>
      </VStack>
    );
  }
  return (
    <Box>
      {buttons}
      <Tabs bg="white" rounded="md" width="100%" size={"lg"}>
        <Center>
          <TabList width="90%">
            <Tab>Description</Tab>
            <Tab>Shared Lore</Tab>
            <Tab>Agents</Tab>
          </TabList>
        </Center>

        <TabPanels>
          <TabPanel>{gamePanel}</TabPanel>
          <TabPanel>
            <GameLore
              existingLore={game.shared_lore ?? []}
              agents={game.agents ?? []}
              handleSave={handleSaveLore}
            ></GameLore>
          </TabPanel>
          <TabPanel>
            <AgentList
              agents={game.agents ?? []}
              addAgent={handleAddAgent}
            ></AgentList>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}

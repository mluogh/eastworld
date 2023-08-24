import {
  Card,
  Text,
  CardHeader,
  CardBody,
  Heading,
  Button,
  Flex,
  Center,
  VStack,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { GameDefinitionsService } from "client";
import { GameDefSummary } from "client";
import { AddIcon, ArrowForwardIcon } from "@chakra-ui/icons";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";

export default function GameList() {
  const [games, setGames] = useState<GameDefSummary[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setGames(await GameDefinitionsService.listGames());
    };
    fetchData();
  }, []);
  const nav = useNavigate();

  const handleAddGame = async () => {
    const game = await GameDefinitionsService.createGame("New Game");
    nav(`game/${game.uuid}`);
  };

  return (
    <VStack spacing={3}>
      <Card
        w="80%"
        onClick={() => handleAddGame()}
        style={{ cursor: "pointer" }}
      >
        <CardHeader>
          <Center>
            <Heading size="md">
              New Game
              <AddIcon marginLeft={3} />
            </Heading>
          </Center>
        </CardHeader>
      </Card>
      {games.map((game, index) => (
        <Card w="80%" key={index}>
          <CardHeader>
            <Flex justifyContent="space-between">
              <Heading size="lg">{game.name}</Heading>
              <Link to={`/game/${game.uuid}`}>
                <Button rightIcon={<ArrowForwardIcon />}>View</Button>
              </Link>
            </Flex>
          </CardHeader>
          <CardBody>
            <Text>{game.description || "No description yet!"}</Text>
          </CardBody>
        </Card>
      ))}
    </VStack>
  );
}

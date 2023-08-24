import {
  Heading,
  IconButton,
  ListItem,
  Text,
  Tooltip,
  UnorderedList,
  VStack,
} from "@chakra-ui/react";
import { InfoIcon } from "@chakra-ui/icons";
import { GameDefinitionsService, Lore } from "client";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

interface LoreProps {
  agentUuid: string;
}

export default function AgentLore(props: LoreProps) {
  const params = useParams();
  const [sharedLore, setSharedLore] = useState<Lore[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const unfiltered = await GameDefinitionsService.getLore(params.gameUuid!);
      const filtered = unfiltered.filter(lore =>
        (lore.known_by ?? []).includes(props.agentUuid),
      );
      setSharedLore(filtered);
    };
    fetchData();
  }, [params.gameUuid, props.agentUuid]);

  return (
    <VStack spacing={4} align={"left"}>
      <Heading size="lg">
        Shared Lore
        <Tooltip
          placement="top"
          label="These are defined in the game editing page."
        >
          <IconButton
            aria-label="Info"
            icon={<InfoIcon />}
            size="lg"
            variant="ghost"
          />
        </Tooltip>
      </Heading>
      {sharedLore.length === 0 && <Text size="lg">No Shared Lore</Text>}
      <UnorderedList>
        {sharedLore.map((lore, index) => (
          <ListItem key={index}>{lore.memory.description}</ListItem>
        ))}
      </UnorderedList>
      <Heading size="lg">Personal Lore</Heading>
      <Text>Deprecated - use shared lore with just 1 Agent.</Text>
    </VStack>
  );
}

import {
  Tooltip,
  FormLabel,
  IconButton,
  Input,
  Grid,
  GridItem,
  Button,
} from "@chakra-ui/react";
import { ArrowRightIcon, InfoIcon } from "@chakra-ui/icons";
import { useState } from "react";
import { GameSessionsService } from "client";
import { useParams } from "react-router-dom";

export default function AgentQuery(props: { sessionUuid: string | undefined }) {
  const [query, setQuery] = useState("");
  const [queryResponse, setQueryResponse] = useState<string>("");

  const params = useParams();

  const getQuery = async () => {
    if (!props.sessionUuid) {
      return;
    }
    let resp = await GameSessionsService.query(
      props.sessionUuid,
      params.agentUuid!,
      [query],
    );

    setQueryResponse(resp[0].toString());
  };

  return (
    <>
      <FormLabel fontSize={"lg"}>
        Query Agent Emotions/Feelings
        <Tooltip
          placement="top"
          label={`Ask a question and an answer on the scale
           of 1-5 will be returned.
          Example format: \n
          "How suspicious of {player} is {agent}?"\n -> 5`}
        >
          <IconButton
            aria-label="Info"
            icon={<InfoIcon />}
            size="xs"
            variant="ghost"
          />
        </Tooltip>
      </FormLabel>
      <Grid templateColumns={"repeat(6, 1fr)"} gap={4}>
        <GridItem colSpan={4}>
          <Input value={query} onChange={e => setQuery(e.target.value)} />
        </GridItem>
        <GridItem>
          <Button
            width="100%"
            leftIcon={<ArrowRightIcon />}
            onClick={() => getQuery()}
          />
        </GridItem>
        <GridItem colSpan={1}>
          <Button width="100%" isDisabled={true}>
            {queryResponse}
          </Button>
        </GridItem>
      </Grid>
    </>
  );
}

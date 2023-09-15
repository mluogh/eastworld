import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";

import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  MessageModel,
  TypingIndicator,
} from "@chatscope/chat-ui-kit-react";
import { useEffect, useState } from "react";
import {
  ActionCompletion,
  AgentDef,
  AgentDefinitionsService,
  Conversation,
  GameSessionsService,
  Message as ClientMessage,
} from "client";
import { useParams } from "react-router-dom";
import {
  Box,
  Button,
  FormControl,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormLabel,
  HStack,
  Select,
  useDisclosure,
  Heading,
  Text,
  Divider,
} from "@chakra-ui/react";
import AgentQuery from "./AgentQuery";
import { ArrowForwardIcon, RepeatIcon } from "@chakra-ui/icons";

export default function Agent() {
  const [sessionUuid, setSessionUuid] = useState<string>();
  const [playableCharacters, setPlayableCharacters] = useState<AgentDef[]>([]);

  const [playerCharacterUuid, setPlayerCharacterUuid] = useState<string>();
  const [chatStarted, setChatStarted] = useState<boolean>(false);

  const [messages, setMessages] = useState<MessageModel[]>([]);
  const [debugMessages, setDebugMessages] = useState<ClientMessage[][]>([]);
  const [debugMessageToShow, setDebugMessageToShow] = useState<ClientMessage[]>(
    [],
  );
  const [waitingForResp, setWaitingForResp] = useState<boolean>(false);

  const params = useParams();

  useEffect(() => {
    const fetchData = async () => {
      const sessUuidCoroutine = GameSessionsService.createSession(
        params.gameUuid!,
      );

      const charactersCoroutine = AgentDefinitionsService.listAgents(
        params.gameUuid!,
      );

      const [sessUuid, characters] = await Promise.all([
        sessUuidCoroutine,
        charactersCoroutine,
      ]);

      const filteredCharacters = characters.filter(
        c => c.is_playable && c.uuid !== params.agentUuid!,
      );
      setPlayableCharacters(filteredCharacters);
      if (filteredCharacters.length > 0) {
        setPlayerCharacterUuid(filteredCharacters[0].uuid);
      }
      setSessionUuid(sessUuid);
    };
    fetchData();
  }, [params]);

  const startChat = async () => {
    const conversation: Conversation = {
      correspondent: playableCharacters.find(
        character => character.uuid === playerCharacterUuid,
      ),
    };
    const emptyChat = { conversation, history: [] };
    await GameSessionsService.startChat(
      sessionUuid!,
      params.agentUuid!,
      "", // todo: use options when generating client
      emptyChat,
    );
    setMessages([]);
    setDebugMessages([]);

    setChatStarted(true);
  };

  const newMessage = (text: string, user: string): MessageModel => {
    return {
      message: text,
      sentTime: "just now",
      direction: user === "user" ? "outgoing" : "incoming",
      position: "single",
      sender: user,
    };
  };

  const newAction = (action: ActionCompletion): MessageModel => {
    const argList = [];
    for (const [key, value] of Object.entries(action.args)) {
      argList.push(`${key}=${value}`);
    }
    const argString = argList.join(", ");
    const message = `${action.action}(${argString})`;
    return {
      message,
      sentTime: "just now",
      direction: "incoming",
      position: "single",
      sender: "action",
    };
  };

  const handleOnSend = async (text: string) => {
    // For some reason, on Firefox it adds <br> at end.
    if (text.endsWith("<br>")) {
      text = text.substring(0, text.lastIndexOf("<br>"));
    }
    setMessages(oldMessages => [...oldMessages, newMessage(text, "user")]);
    setWaitingForResp(true);

    const interact = await GameSessionsService.interact(
      sessionUuid!,
      params.agentUuid!,
      text,
      /*sendDebug=*/ true,
    );

    setWaitingForResp(false);
    const response = interact.response;

    if ("content" in response) {
      setMessages(oldMessages => [
        ...oldMessages,
        newMessage(response.content, "assistant"),
      ]);
    } else {
      setMessages(oldMessages => [...oldMessages, newAction(response)]);
    }

    setDebugMessages(oldMessages => [...oldMessages, interact.debug ?? []]);
  };

  const { isOpen, onOpen, onClose } = useDisclosure();

  const showDebugModal = (index: number) => {
    if (index % 2 === 0) {
      return;
    }
    setDebugMessageToShow(debugMessages[Math.floor(index / 2)]);
    onOpen();
  };

  return (
    <Box pos="fixed" left="50%" height="60%" width="35%">
      <HStack marginBottom={3}>
        <FormControl width="70%">
          <HStack spacing={10}>
            <FormLabel
              htmlFor="option-select"
              whiteSpace="nowrap"
              marginBottom={0}
              width={"max-content"}
            >
              Speak as:
            </FormLabel>
            <Select
              id="character-select"
              placeholder="Select playable character"
              value={playerCharacterUuid}
              onChange={e => setPlayerCharacterUuid(e.target.value)}
            >
              {playableCharacters.map((character, index) => (
                <option value={character.uuid} key={index}>
                  {character.name}
                </option>
              ))}
            </Select>
          </HStack>
        </FormControl>
        <Button
          colorScheme={chatStarted ? "gray" : "purple"}
          rightIcon={chatStarted ? <RepeatIcon /> : <ArrowForwardIcon />}
          isDisabled={!playerCharacterUuid}
          onClick={startChat}
          width={"30%"}
        >
          {chatStarted ? "Restart" : "Start"}
        </Button>
      </HStack>
      <MainContainer>
        <ChatContainer>
          <MessageList
            typingIndicator={
              waitingForResp ? (
                <TypingIndicator content="Agent is thinking" />
              ) : null
            }
          >
            {messages.map((message, index) => (
              <Message
                key={index}
                model={message}
                onClick={() => showDebugModal(index)}
                style={index % 2 === 1 ? { cursor: "pointer" } : undefined}
              >
                {message.sender === "action" && (
                  <Message.Footer sender="Action Completion" />
                )}
              </Message>
            ))}
          </MessageList>
          <MessageInput
            disabled={!chatStarted}
            placeholder={
              chatStarted ? "Type message here" : "Start a session to chat"
            }
            onSend={text => handleOnSend(text)}
          />
        </ChatContainer>
      </MainContainer>
      <Box marginTop={7}>
        <AgentQuery sessionUuid={sessionUuid}></AgentQuery>
      </Box>
      <Modal size="3xl" isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>LLM Prompt for Message</ModalHeader>
          <ModalCloseButton />
          <ModalBody width={"100%"} whiteSpace={"pre-line"}>
            {debugMessageToShow.map((message, index) => (
              <Box key={index}>
                <Heading size="md">{message.role}</Heading>
                <Text size="lg">{message.content}</Text>
                <Divider margin={5}></Divider>
              </Box>
            ))}
          </ModalBody>

          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
}

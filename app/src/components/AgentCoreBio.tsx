import { useFormik } from "formik";
import {
  Editable,
  EditablePreview,
  EditableInput,
  EditableTextarea,
  Heading,
  FormLabel,
  Text,
  Tooltip,
  IconButton,
} from "@chakra-ui/react";

import * as Yup from "yup";
import { AgentDef } from "client";
import { ColoredPreview } from "util/ColoredPreview";
import { InfoIcon } from "@chakra-ui/icons";
import { useRef } from "react";

interface AutoResizeEditableProps {
  value: string | undefined;
  name: string;
  placeholder: string;
  handleSubmit: any;
  handleChange: any;
}

function AutoResizeEditable(props: AutoResizeEditableProps) {
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const resizeTextArea = () => {
    textAreaRef.current!.style.height = "auto";
    textAreaRef.current!.style.height =
      textAreaRef.current!.scrollHeight + "px";
  };

  return (
    <Editable
      value={props.value}
      onSubmit={() => props.handleSubmit()}
      placeholder={props.placeholder}
      color={props.value ? "black" : "gray"}
    >
      <ColoredPreview height="max-content" minHeight="10em" />
      <EditableTextarea
        ref={textAreaRef}
        rows={5}
        name={props.name}
        onChange={e => {
          resizeTextArea();
          props.handleChange(e);
        }}
      />
    </Editable>
  );
}

const AgentDefSchema = Yup.object().shape({
  is_playable: Yup.bool(),
  name: Yup.string().required("Required"),
  description: Yup.string(),
  example_speech: Yup.string(),
  instructions: Yup.string(),
  core_facts: Yup.string(),
});

export type AgentCoreBioSubset = Yup.InferType<typeof AgentDefSchema>;

interface AgentCoreBioProps {
  agent: AgentDef;
  handleSave: (def: AgentCoreBioSubset) => Promise<void>;
}
export default function AgentCoreBio(props: AgentCoreBioProps) {
  const formik = useFormik({
    initialValues: {
      is_playable: props.agent.is_playable,
      name: props.agent.name,
      description: props.agent.description ?? "",
      core_facts: props.agent.core_facts,
      instructions: props.agent.instructions,
      example_speech: props.agent.example_speech,
    },
    validationSchema: AgentDefSchema,
    onSubmit: async values => {
      await props.handleSave(values);
    },
  });

  let descriptionHeading,
    descriptionPlaceholder,
    llmInstructionHeader,
    llmInstructionPlaceholder;

  if (props.agent.is_playable) {
    descriptionHeading = "Appearance & Reputation";
    descriptionPlaceholder =
      "A description of the player that other agents will be given during conversations.";
    llmInstructionHeader = "Player Guardrail Instructions";
    llmInstructionPlaceholder =
      `Instructions for the guardrail() endpoint that will ` +
      `moderate user conversation. Write as though you were speaking to the player.
E.g.
You MUST not behave aggressively.
You MUST not mention modern technology.`;
  } else {
    descriptionHeading = "Description & Personality";
    descriptionPlaceholder = `A description of the agent that the LLM can use to generate a convincing persona.
e.g.
Occupation: Revolutionary
Age: 40
Personality: Forceful, stoic, loyal, idealistic, ...
Core Beliefs: 
Believes in freedom for all.
...
`;
    llmInstructionHeader = "Agent Instructions";
    llmInstructionPlaceholder = `Instructions for how the LLM should behave. Write in second person. 
e.g. 
You MUST speak with a Brooklyn accent.
You MUST not reveal your hidden affiliation with the Green Dragon clan.`;
  }

  return (
    <>
      <Editable
        fontSize="6xl"
        fontWeight="bold"
        value={formik.values.name}
        onSubmit={() => formik.handleSubmit()}
      >
        <EditablePreview width="full" cursor="pointer" />
        <EditableInput name="name" onChange={formik.handleChange} />
      </Editable>
      {formik.errors.name && <Text color="red.500">{formik.errors.name}</Text>}
      <FormLabel marginBottom={8}>
        Is playable character:
        <input
          type="checkbox"
          name="is_playable"
          checked={formik.values.is_playable}
          onChange={e => {
            formik.handleChange(e);
            formik.submitForm();
          }}
        />
      </FormLabel>
      <Heading size="xl" marginBottom={5}>
        Biography
        <Tooltip
          placement="top"
          label={`Details about the agent that will be given to the LLM in every
            conversation they have. Try to keep each field short and concise to
            keep inference costs low. You can use the "Lore" tab to add more
            details.`}
        >
          <IconButton
            aria-label="Info"
            icon={<InfoIcon />}
            size="lg"
            variant="ghost"
          />
        </Tooltip>
      </Heading>
      <Heading size="lg">- {descriptionHeading}</Heading>
      {formik.errors.description && (
        <Text color="red.500">{formik.errors.description}</Text>
      )}
      <AutoResizeEditable
        value={formik.values.description}
        placeholder={descriptionPlaceholder}
        name="description"
        handleSubmit={formik.handleSubmit}
        handleChange={formik.handleChange}
      ></AutoResizeEditable>
      {!props.agent.is_playable && (
        <>
          <Heading size="lg"> - Core Knowledge</Heading>
          <AutoResizeEditable
            value={formik.values.core_facts}
            placeholder="Important facts that the agent knows that will be included in every conversation. E.g.: 
Write in third person.
He has a dog named Biscuit.
He has a brother named Tim."
            name="core_facts"
            handleSubmit={formik.handleSubmit}
            handleChange={formik.handleChange}
          ></AutoResizeEditable>
        </>
      )}
      <Heading size="lg"> - {llmInstructionHeader}</Heading>
      <AutoResizeEditable
        value={formik.values.instructions}
        placeholder={llmInstructionPlaceholder}
        name="instructions"
        handleSubmit={formik.handleSubmit}
        handleChange={formik.handleChange}
      ></AutoResizeEditable>
      {!props.agent.is_playable && (
        <>
          <Heading size="lg"> - Example Speech</Heading>
          <AutoResizeEditable
            value={formik.values.example_speech}
            placeholder={`Example dialog of how the character speaks, one example per line.
3-4 should be enough.
e.g.
Ah fuhgedaboutit!
Not for nuttin' but you're outta line.
Get a load a dis guy ovah here!`}
            name="example_speech"
            handleSubmit={formik.handleSubmit}
            handleChange={formik.handleChange}
          ></AutoResizeEditable>
        </>
      )}
    </>
  );
}

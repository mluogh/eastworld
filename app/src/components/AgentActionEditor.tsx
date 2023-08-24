import {
  Flex,
  Text,
  Input,
  FormControl,
  FormLabel,
  Select,
  Box,
  Button,
  Heading,
  Tooltip,
  IconButton,
} from "@chakra-ui/react";

import { useToast } from "@chakra-ui/react";
import { Action } from "client";
import Form from "@rjsf/chakra-ui";
import { UtilService } from "client";
import { useEffect, useState } from "react";

import { RJSFSchema, WidgetProps, ArrayFieldTemplateProps } from "@rjsf/utils";
import validator from "@rjsf/validator-ajv8";
import { AddIcon, DeleteIcon, InfoIcon } from "@chakra-ui/icons";

function ArrayFieldTemplate(text: string) {
  return (props: ArrayFieldTemplateProps) => {
    return (
      <div>
        {props.items.map(element => (
          <div key={element.key} className={element.className}>
            {element.children}
            <Box display="flex" justifyContent="flex-end">
              <Button
                leftIcon={<DeleteIcon />}
                onClick={element.onDropIndexClick(element.index)}
              >
                {text}
              </Button>
            </Box>
          </div>
        ))}

        <Box display="flex" justifyContent="space-between">
          {props.canAdd && (
            <Button leftIcon={<AddIcon />} onClick={props.onAddClick}>
              {text}
            </Button>
          )}
        </Box>
      </div>
    );
  };
}

const LabelBySide = (props: WidgetProps) => {
  return (
    <FormControl>
      <Flex alignItems="center">
        <FormLabel mb="0" mr="3">
          {props.name}
          {props.required && (
            <Text as="span" color="red">
              *
            </Text>
          )}
        </FormLabel>
        <Input
          id={props.id}
          type="text"
          onChange={event => props.onChange(event.target.value)}
          value={props.value}
        />
      </Flex>
    </FormControl>
  );
};

const LabelBySideSelect = (props: WidgetProps) => {
  const { id, label, required, onChange, options, value } = props;

  return (
    <FormControl display="flex" alignItems="center">
      <FormLabel htmlFor={id} mb="0" mr="3">
        {label}
        {required && (
          <Text as="span" color="red">
            *
          </Text>
        )}
      </FormLabel>
      <Select
        id={id}
        onChange={event => onChange(event.target.value)}
        value={value}
      >
        {options.enumOptions!.map((option, i) => (
          <option key={i} value={option.value}>
            {option.label}
          </option>
        ))}
      </Select>
    </FormControl>
  );
};

interface ActionEditorProps {
  actions: Action[];
  handleSave: (actions: Action[]) => Promise<void>;
}

export default function AgentActionEditor(props: ActionEditorProps) {
  const [schema, setSchema] = useState<RJSFSchema>({});
  const [actions, setActions] = useState<Action[]>([]);

  const toast = useToast();

  useEffect(() => {
    const fetchData = async () => {
      const actionSchema = JSON.parse(await UtilService.getActionJsonSchema());
      setSchema({
        type: "array",
        items: actionSchema,
        definitions: actionSchema.definitions,
      });
    };
    fetchData();
  }, []);

  useEffect(() => {
    setActions(JSON.parse(JSON.stringify(props.actions)));
  }, [props.actions]);

  const uiSchema = {
    items: {
      "ui:classNames": "small-title",
      parameters: {
        items: {
          enum: {
            "ui:title": "Enum (optional)",
          },
        },
        "ui:ArrayFieldTemplate": ArrayFieldTemplate("Parameter"),
      },
    },
    "ui:submitButtonOptions": {
      submitText: "Save",
    },
    "ui:ArrayFieldTemplate": ArrayFieldTemplate("Action"),
  };

  const widgets = {
    TextWidget: LabelBySide,
    SelectWidget: LabelBySideSelect,
  };

  return (
    <>
      <style>
        {`
        .small-title .chakra-heading {
          font-size: 20px;)
        }
      `}
      </style>
      <Heading size={"lg"}>
        Actions
        <Tooltip
          placement="top"
          label="Actions that the agents can take instead of responding to the 
          player with text. These can be called if you use the interact() 
          endpoints and will be called if you call the act() endpoint. 
          E.g. agents can have an Attack() function that the LLM may choose 
          to call if the player threatens them."
        >
          <IconButton
            aria-label="Info"
            icon={<InfoIcon />}
            size="lg"
            variant="ghost"
          />
        </Tooltip>
      </Heading>
      <Form
        autoComplete="off"
        uiSchema={uiSchema}
        schema={schema}
        formData={actions}
        validator={validator}
        widgets={widgets}
        onSubmit={({ formData }) => {
          setActions(formData);
          props.handleSave(formData);
          toast({
            title: "Actions saved!",
            status: "success",
            duration: 2000,
            isClosable: true,
          });
        }}
      >
        <Button marginTop={8} width={"100%"} type="submit" colorScheme="purple">
          Save
        </Button>
      </Form>
    </>
  );
}

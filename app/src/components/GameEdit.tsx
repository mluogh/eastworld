import { useFormik } from "formik";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Textarea,
  HStack,
  Spacer,
} from "@chakra-ui/react";

import * as Yup from "yup";
import { GameDef } from "client";

const GameDefSchema = Yup.object().shape({
  name: Yup.string().required("Required"),
  description: Yup.string().required("Required"),
});

export type GameDefSubset = Yup.InferType<typeof GameDefSchema>;

interface GameEditProps {
  game: GameDef;
  handleSave: (def: GameDefSubset) => Promise<void>;
  handleCancel: () => void;
}

export default function GameEdit(props: GameEditProps) {
  const formik = useFormik({
    initialValues: {
      name: props.game.name,
      description: props.game.description ?? "",
    },
    validationSchema: GameDefSchema,
    onSubmit: values => {
      props.handleSave(values);
    },
  });

  return (
    <Box bg="white" p={6} rounded="md" width={"100%"}>
      <form onSubmit={formik.handleSubmit}>
        <VStack spacing={4} align="flex-start">
          <FormControl>
            <FormLabel htmlFor="name">Name</FormLabel>
            <Input
              id="name"
              name="name"
              type="name"
              variant="filled"
              onChange={formik.handleChange}
              value={formik.values.name}
            />
          </FormControl>
          <FormControl>
            <FormLabel htmlFor="description">Description</FormLabel>
            <Textarea
              id="description"
              name="description"
              variant="filled"
              rows={10}
              placeholder="A description of the game that every agent will see. It should describe the tone of the game world."
              onChange={formik.handleChange}
              value={formik.values.description}
            />
          </FormControl>
          <HStack width="full">
            <Button onClick={() => props.handleCancel()} colorScheme="red">
              Cancel
            </Button>
            <Spacer />
            <Button type="submit" colorScheme="purple">
              Save
            </Button>
          </HStack>
        </VStack>
      </form>
    </Box>
  );
}

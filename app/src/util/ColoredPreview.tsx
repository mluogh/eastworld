import { EditablePreview } from "@chakra-ui/react";
import { styled } from "styled-components";

export const ColoredPreview = styled(EditablePreview)`
  background-color: #f0f0f0;
  white-space: pre-line;
  overflow: auto;
  width: 100%;
  cursor: pointer;
  padding-left: 5px;
  padding-right: 5px;
`;

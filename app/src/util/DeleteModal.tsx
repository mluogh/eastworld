import {
  Button,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
} from "@chakra-ui/react";
import { DeleteIcon } from "@chakra-ui/icons";

type DeleteModalProps = {
  text: string;
  onDelete: () => void;
};

const DeleteModal = ({ text, onDelete }: DeleteModalProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const handleDelete = () => {
    onDelete();
    onClose();
  };

  return (
    <>
      <IconButton
        onClick={onOpen}
        icon={<DeleteIcon />}
        colorScheme="red"
        aria-label="delete"
      />

      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Confirm Deletion</ModalHeader>
          <ModalCloseButton />
          <ModalBody>{text}</ModalBody>
          <ModalFooter>
            <Button colorScheme="red" mr={3} onClick={handleDelete}>
              Delete
            </Button>
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default DeleteModal;

import {
  Tabs,
  Tab,
  TabPanels,
  TabPanel,
  TabList,
  Center,
} from "@chakra-ui/react";

import { AgentDef } from "client";
import { useState } from "react";
import { Action } from "client";
import AgentActionEditor from "./AgentActionEditor";
import AgentLore from "./AgentLore";
import AgentCoreBio, { AgentCoreBioSubset } from "./AgentCoreBio";

interface AgentEditProps {
  agent: AgentDef;
  handleSave: (def: AgentDef) => Promise<void>;
}

export default function AgentEdit(props: AgentEditProps) {
  // So the actions doesn't keep reloading.
  const [actions, setActions] = useState<Action[]>(props.agent.actions ?? []);

  const saveCoreBio = async (subset: AgentCoreBioSubset) => {
    await props.handleSave({ ...props.agent, ...subset });
  };

  const saveActions = async (actions: Action[]) => {
    setActions(actions);
    await props.handleSave({ ...props.agent, actions });
  };

  return (
    <Tabs bg="white" rounded="md" width="100%">
      <Center>
        <TabList width="90%">
          <Tab>Core Bio</Tab>
          <Tab>Lore</Tab>
          <Tab>Actions</Tab>
        </TabList>
      </Center>

      <TabPanels>
        <TabPanel>
          <AgentCoreBio agent={props.agent} handleSave={saveCoreBio} />
        </TabPanel>
        <TabPanel>
          <AgentLore agentUuid={props.agent.uuid!} />
        </TabPanel>
        <TabPanel>
          <AgentActionEditor
            actions={actions}
            handleSave={saveActions}
          ></AgentActionEditor>
        </TabPanel>
      </TabPanels>
    </Tabs>
  );
}

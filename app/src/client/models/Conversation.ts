/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AgentDef } from './AgentDef';

export type Conversation = {
    correspondent?: AgentDef;
    scene_description?: string;
    instructions?: string;
    queries?: Array<string>;
    memories_to_include?: number;
};


/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Action } from './Action';
import type { Memory } from './Memory';

export type AgentDef = {
    uuid?: string;
    is_playable?: boolean;
    name: string;
    description?: string;
    core_facts?: string;
    instructions?: string;
    example_speech?: string;
    personal_lore?: Array<Memory>;
    actions?: Array<Action>;
};


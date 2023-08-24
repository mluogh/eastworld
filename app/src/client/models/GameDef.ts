/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AgentDef } from './AgentDef';
import type { Lore } from './Lore';

export type GameDef = {
    uuid?: string;
    name: string;
    description?: string;
    agents?: Array<AgentDef>;
    shared_lore?: Array<Lore>;
};


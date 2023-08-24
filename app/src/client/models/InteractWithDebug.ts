/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ActionCompletion } from './ActionCompletion';
import type { Message } from './Message';

export type InteractWithDebug = {
    response: (Message | ActionCompletion);
    debug?: Array<Message>;
};


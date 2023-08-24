/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActionCompletion } from '../models/ActionCompletion';
import type { Body_start_chat } from '../models/Body_start_chat';
import type { InteractWithDebug } from '../models/InteractWithDebug';
import type { MessageWithDebug } from '../models/MessageWithDebug';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class GameSessionsService {

    /**
     * Create Session
     * @param gameUuid
     * @returns string Successful Response
     * @throws ApiError
     */
    public static createSession(
        gameUuid: string,
    ): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/session/create',
            query: {
                'game_uuid': gameUuid,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Sessions List
     * @param gameUuid
     * @returns string Successful Response
     * @throws ApiError
     */
    public static listSessions(
        gameUuid: string,
    ): CancelablePromise<Array<string>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/session/list',
            query: {
                'game_uuid': gameUuid,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Start Conversation
     * @param sessionUuid
     * @param agent
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static startChat(
        sessionUuid: string,
        agent: string,
        requestBody: Body_start_chat,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/session/{session_uuid}/start_chat',
            path: {
                'session_uuid': sessionUuid,
            },
            query: {
                'agent': agent,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Chat
     * @param sessionUuid
     * @param agent
     * @param message
     * @param sendDebug
     * @returns MessageWithDebug Successful Response
     * @throws ApiError
     */
    public static chat(
        sessionUuid: string,
        agent: string,
        message: string,
        sendDebug: boolean = false,
    ): CancelablePromise<MessageWithDebug> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/session/{session_uuid}/chat',
            path: {
                'session_uuid': sessionUuid,
            },
            query: {
                'agent': agent,
                'message': message,
                'send_debug': sendDebug,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Interact
     * @param sessionUuid
     * @param agent
     * @param message
     * @param sendDebug
     * @returns InteractWithDebug Successful Response
     * @throws ApiError
     */
    public static interact(
        sessionUuid: string,
        agent: string,
        message: string,
        sendDebug: boolean = false,
    ): CancelablePromise<InteractWithDebug> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/session/{session_uuid}/interact',
            path: {
                'session_uuid': sessionUuid,
            },
            query: {
                'agent': agent,
                'message': message,
                'send_debug': sendDebug,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Act
     * @param sessionUuid
     * @param agent
     * @param message
     * @param sendDebug
     * @returns ActionCompletion Successful Response
     * @throws ApiError
     */
    public static action(
        sessionUuid: string,
        agent: string,
        message: string,
        sendDebug: boolean = false,
    ): CancelablePromise<ActionCompletion> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/session/{session_uuid}/act',
            path: {
                'session_uuid': sessionUuid,
            },
            query: {
                'agent': agent,
                'message': message,
                'send_debug': sendDebug,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Guardrail
     * @param sessionUuid
     * @param agent
     * @param message
     * @returns number Successful Response
     * @throws ApiError
     */
    public static guardrail(
        sessionUuid: string,
        agent: string,
        message: string,
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/session/{session_uuid}/guardrail',
            path: {
                'session_uuid': sessionUuid,
            },
            query: {
                'agent': agent,
                'message': message,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Query
     * @param sessionUuid
     * @param agent
     * @param requestBody
     * @returns number Successful Response
     * @throws ApiError
     */
    public static query(
        sessionUuid: string,
        agent: string,
        requestBody: Array<string>,
    ): CancelablePromise<Array<number>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/session/{session_uuid}/query',
            path: {
                'session_uuid': sessionUuid,
            },
            query: {
                'agent': agent,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Updatesessions
     * @param gameUuid
     * @returns any Successful Response
     * @throws ApiError
     */
    public static syncSessionsToGameDefs(
        gameUuid: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/session/sync',
            query: {
                'game_uuid': gameUuid,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}

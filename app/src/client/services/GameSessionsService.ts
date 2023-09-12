/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActionCompletionWithDebug } from '../models/ActionCompletionWithDebug';
import type { Body_start_chat } from '../models/Body_start_chat';
import type { InteractWithDebug } from '../models/InteractWithDebug';
import type { MessageWithDebug } from '../models/MessageWithDebug';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class GameSessionsService {

    /**
     * Create Session
     * Given a Game, creates a game session and populates the Agents
     * with their lore and knowledge.
     *
     * <h3>Args:</h3>
     *
     * - **game_uuid** (uuid4 as str): The uuid of the GameDef that this session will
     * populate from.
     *
     * <h3>Returns:</h3>
     * - **session_uuid** (uuid4 as str): the uuid of the session created
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
     * Lists all active sessions for a given Game.
     *
     * <h3>Args:</h3>
     *
     * - **game_uuid** (uuid4 as str): The uuid of the GameDef
     *
     * <h3>Returns:</h3>
     * - **session_uuids** (List[uuid4] as List[str]): the uuids of the sessions
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
     * Starts a chat with the given agent. Clears previous conversation
     * history.
     *
     * <h3>Args:</h3>
     *
     * - **session_uuid** (str): the uuid of the session
     * - **agent** (str): either the uuid or the name of the agent.
     * - **correspondent** (str): the character with whom the agent is speaking to.
     * - **conversation** (Conversation): conversation context. See definition.
     * - **history** List[Message]: pre-populate the conversation so you start
     * as though you were mid-conversation
     *
     * <h3>Returns:</h3>
     * - none
     * @param sessionUuid
     * @param agent
     * @param correspondent
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static startChat(
        sessionUuid: string,
        agent: string,
        correspondent?: string,
        requestBody?: Body_start_chat,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/session/{session_uuid}/start_chat',
            path: {
                'session_uuid': sessionUuid,
            },
            query: {
                'agent': agent,
                'correspondent': correspondent,
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
     * Sends `message` to the given agent. They will respond with text.
     *
     * <h3>Args:</h3>
     *
     * - **session_uuid** (str): the uuid of the session
     * - **agent** (str): either the uuid or the name of the agent.
     * - **message** (str): what you're saying to the agent
     * - **send_debug** (bool): sends optional debugging information
     *
     * <h3>Returns:</h3>
     * - **message_with_debug** (MessageWithDebug): returned completion is in
     * message_with_debug.message.content. Optional debug information in
     * message_with_debug.debug.
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
     * Sends message to the given agent. They will respond with
     * an Action or text.
     *
     * <h3>Args:</h3>
     *
     * - **session_uuid** (str): the uuid of the session
     * - **agent** (str): either the uuid or the name of the agent.
     * - **message** (str): what you're saying to the agent
     * - **send_debug** (bool): sends optional debugging information
     *
     * <h3>Returns:</h3>
     * - **response_with_debug** (ResponseWithDebug): returned completion
     * response_with_debug.response can either be a Message or an
     * ActionCompletion
     * Optional debug information in message_with_debug.debug.
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
     * Asks the given agent to perform an action. Optionally
     * after sending a message.
     *
     * <h3>Args:</h3>
     *
     * - **session_uuid** (str): the uuid of the session
     * - **agent** (str): either the uuid or the name of the agent.
     * - **message** (Optional[str]): what you're saying to the agent
     * - **send_debug** (bool): sends optional debugging information
     *
     * <h3>Returns:</h3>
     * - **action_with_debug** (ActionCompletionWithDebug): returned completion
     * in response_with_debug.action.
     * Optional debug information in message_with_debug.debug.
     * @param sessionUuid
     * @param agent
     * @param message
     * @param sendDebug
     * @returns ActionCompletionWithDebug Successful Response
     * @throws ApiError
     */
    public static action(
        sessionUuid: string,
        agent: string,
        message: string,
        sendDebug: boolean = false,
    ): CancelablePromise<ActionCompletionWithDebug> {
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
     * Asks whether or not what the player is saying is appropriate given
     * the time period, tone, and intent of the game.
     *
     * <h3>Args:</h3>
     *
     * - **session_uuid** (str): the uuid of the session
     * - **agent** (str): either the uuid or the name of the agent.
     * - **message** (Optional[str]): what the player is trying to say to the agent
     *
     * <h3>Returns:</h3>
     * - **appropriateness** (int): number from 1-5. 1 = very inappropriate,
     * 5 = very appropriate. Return -1 on LLM error
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
     * Responds to queries into how the Agent is feeling during conversation
     * with the player. Write in second person. You can use {player} to refer
     * to the player character (since there can be several).
     *
     * e.g.
     * - How suspicious are you that {player} is onto him?
     * - How happy are you?
     * - How angry are you with {player}?
     *
     * Phrase queries in a way such that responses like "not at all" or "extremely"
     * make sense.
     *
     * <h3>Args:</h3>
     *
     * - **session_uuid** (str): the uuid of the session
     * - **agent** (str): either the uuid or the name of the agent.
     * - **queries** (List[str]): list of queries you want to know about agent
     *
     * <h3>Returns:</h3>
     * - **appropriateness** (List[int]): number from 1-5. 1 = not at all,
     * 5 = extremely. Returns -1 on LLM error
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

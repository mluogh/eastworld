/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GameDef } from '../models/GameDef';
import type { GameDefSummary } from '../models/GameDefSummary';
import type { Lore } from '../models/Lore';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class GameDefinitionsService {

    /**
     * Create Game Def
     * @param gameName
     * @returns GameDef Successful Response
     * @throws ApiError
     */
    public static createGame(
        gameName: string,
    ): CancelablePromise<GameDef> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/game/create',
            query: {
                'game_name': gameName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Games List
     * @returns GameDefSummary Successful Response
     * @throws ApiError
     */
    public static listGames(): CancelablePromise<Array<GameDefSummary>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/game/list',
        });
    }

    /**
     * Get Game Def
     * @param uuid
     * @returns GameDef Successful Response
     * @throws ApiError
     */
    public static getGame(
        uuid: string,
    ): CancelablePromise<GameDef> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/game/{uuid}',
            path: {
                'uuid': uuid,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Game Def
     * @param uuid
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteGame(
        uuid: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/game/{uuid}',
            path: {
                'uuid': uuid,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Game Lore
     * @param uuid
     * @returns Lore Successful Response
     * @throws ApiError
     */
    public static getLore(
        uuid: string,
    ): CancelablePromise<Array<Lore>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/game/{uuid}/lore',
            path: {
                'uuid': uuid,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Game Def Json
     * @param uuid
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getGameJson(
        uuid: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/game/{uuid}/json',
            path: {
                'uuid': uuid,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Game Def Json
     * @param jsonedGame
     * @returns any Successful Response
     * @throws ApiError
     */
    public static createGameJson(
        jsonedGame: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/game/json',
            query: {
                'jsoned_game': jsonedGame,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Game Def
     * @param uuid
     * @param requestBody
     * @param overwriteAgents
     * @returns GameDef Successful Response
     * @throws ApiError
     */
    public static updateGame(
        uuid: string,
        requestBody: GameDef,
        overwriteAgents: boolean = false,
    ): CancelablePromise<GameDef> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/game/{uuid}/update',
            path: {
                'uuid': uuid,
            },
            query: {
                'overwrite_agents': overwriteAgents,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}

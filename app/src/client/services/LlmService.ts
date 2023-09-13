/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class LlmService {

    /**
     * Embed
     * @param text
     * @returns number Successful Response
     * @throws ApiError
     */
    public static embed(
        text: string,
    ): CancelablePromise<Array<number>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/llm/embed',
            query: {
                'text': text,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Rate
     * @param question
     * @returns number Successful Response
     * @throws ApiError
     */
    public static rate(
        question: string,
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/llm/rate',
            query: {
                'question': question,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}

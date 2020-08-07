/*
 * Copyright (C) 2018 ETH Zurich, University of Bologna and GreenWaves Technologies
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef __PMSIS_TASK_H__
#define __PMSIS_TASK_H__

#include "pmsis/pmsis_types.h"

pi_task_t *pi_task_callback(pi_task_t *callback_task, void (*callback)(void*), void *arg);

pi_task_t *pi_task_callback_no_mutex(pi_task_t *callback_task, void (*func)(void *), void *arg);

static inline pi_task_t *pi_task_block(pi_task_t *callback_task);

pi_task_t *pi_task_block_no_mutex(pi_task_t *callback_task);

static inline void pi_task_destroy(pi_task_t *task);

void pi_task_push(pi_task_t *task);

void pi_task_push_delayed_us(pi_task_t *task, uint32_t delay);

void pi_task_release(pi_task_t *task);

/**
 * Wait on the execution of the task associated to pi_task_t
 * Task must already have been initialized
 **/
void pi_task_wait_on(pi_task_t *task);

void pi_task_wait_on_no_mutex(pi_task_t *task);

#ifdef PMSIS_DRIVERS

//#include "pmsis_hal/pmsis_hal.h"
#include "pmsis_backend/pmsis_backend_native_task_api.h"
pi_task_t *__pi_task_block(pi_task_t *callback_task);

static inline struct pi_task *pi_task_block(struct pi_task *callback_task)
{
    __pi_task_block(callback_task);
    return callback_task;
}

void __pi_task_destroy(pi_task_t *task);

static inline void pi_task_destroy(pi_task_t *task)
{
    __pi_task_destroy(task);
}

#endif

#endif  /* __PMSIS_TASK_H__ */

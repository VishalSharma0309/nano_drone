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

#ifndef __PMSIS_L1_MALLOC_H__
#define __PMSIS_L1_MALLOC_H__

#include "pmsis/rtos/malloc/pmsis_malloc_internal.h"

void *pmsis_l1_malloc(uint32_t size);

void pmsis_l1_malloc_free(void *_chunk, int size);

void *pmsis_l1_malloc_align(int size, int align);

void pmsis_l1_malloc_init(void *heapstart, uint32_t size);

void pmsis_l1_malloc_set_malloc_struct(malloc_t malloc_struct);

malloc_t pmsis_l1_malloc_get_malloc_struct(void);

#endif  /* __PMSIS_L1_MALLOC_H__ */

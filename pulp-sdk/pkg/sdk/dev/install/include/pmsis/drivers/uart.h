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


#ifndef _PMSIS_UART_H_
#define _PMSIS_UART_H_

#include "pmsis/pmsis_types.h"

/*!
 * @addtogroup uart_driver
 * @{
 */

/*******************************************************************************
 * Definitions
 ******************************************************************************/

/*! @name Driver version */
/*@{*/
/*! @brief UART driver version 1.0.0. */
/*@}*/


/*! @brief UART configuration structure. */

struct pi_uart_conf
{
    uint32_t src_clock_Hz;
    uint32_t baudrate_bps;
    uint32_t stop_bit_count; /*!< Number of stop bits, 1 stop bit (default) or 2 stop bits  */
    uint8_t parity_mode;
    uint8_t uart_id;
    uint8_t enable_rx;
    uint8_t enable_tx;
};

typedef struct pi_cl_uart_req_s pi_cl_uart_req_t;

/*******************************************************************************
 * API
 ******************************************************************************/

#if defined(__cplusplus)
extern "C" {
#endif /* _cplusplus */


void pi_uart_conf_init(struct pi_uart_conf *conf);

int pi_uart_open(struct pi_device *device);

int pi_uart_write(struct pi_device *device, void *buffer, uint32_t size);

int pi_uart_write_async(struct pi_device *device, void *buffer, uint32_t size, pi_task_t* callback);

int pi_uart_read(struct pi_device *device, void *buffer, uint32_t size);

int pi_uart_read_async(struct pi_device *device, void *buffer, uint32_t size, pi_task_t* callback);

int pi_uart_write_byte(struct pi_device *device, uint8_t *byte);

int pi_uart_write_byte_async(struct pi_device *device, uint8_t *byte, pi_task_t* callback);

int pi_uart_read_byte(struct pi_device *device, uint8_t *byte);

void pi_uart_close(struct pi_device *device);


// cluster counterparts

int pi_cl_uart_write(pi_device_t *device, void *buffer, uint32_t size, pi_cl_uart_req_t *req);

int pi_cl_uart_write_byte(pi_device_t *device, uint8_t *byte, pi_cl_uart_req_t *req);

static inline void pi_cl_hyperram_write_wait(pi_cl_uart_req_t *req);

int pi_cl_uart_read(pi_device_t *device, void *addr, uint32_t size, pi_cl_uart_req_t *req);

int pi_cl_uart_read_byte(pi_device_t *device, uint8_t *byte, pi_cl_uart_req_t *req);

static inline void pi_cl_uart_read_wait(pi_cl_uart_req_t *req);



/*!
 * @brief Gets the default configuration structure.
 *
 * This function initializes the UART configuration structure to a default value.
 *
 * @param config Pointer to configuration structure.
 */
void pi_uart_conf_init(struct pi_uart_conf *conf);

/* @} */

#if defined(__cplusplus)
}
#endif

/*! @}*/

#endif /* _GAP_UART_H_ */

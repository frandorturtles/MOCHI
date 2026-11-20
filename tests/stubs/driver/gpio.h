#pragma once
typedef int gpio_num_t;
#define GPIO_INTR_LOW_LEVEL 4
inline void gpio_wakeup_enable(gpio_num_t, int) {}

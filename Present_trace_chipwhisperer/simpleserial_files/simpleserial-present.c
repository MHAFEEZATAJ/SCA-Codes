#include "hal.h"
#include "simpleserial.h"
#include <string.h>
#include <stdint.h>
#include "present.h"

uint8_t key[10];  // 80-bit key

// Set the key from the host (command 'k')
uint8_t set_key(uint8_t *k, uint8_t len) {
    if (len != 10) return 0; // Expecting 80-bit key
    memcpy(key, k, 10);
    return 0;
}

// Encrypt a plaintext block (command 'p') and return ciphertext
uint8_t encrypt_block(uint8_t *pt, uint8_t len) {
    if (len != 8) return 0; // Expecting 64-bit plaintext

    uint8_t block[8];
    memcpy(block, pt, 8);

    trigger_high();
    present_encrypt(block,key); // In-place encryption
    trigger_low();

    simpleserial_put('r', 8, block); // Return ciphertext
    return 0;
}

int main(void) {
    platform_init();
    init_uart();
    trigger_setup();
    simpleserial_init();

    simpleserial_addcmd('k', 10, set_key);  // 80-bit key
    simpleserial_addcmd('p', 8, encrypt_block); // 64-bit plaintext

    while(1)
        simpleserial_get();
}
#ifndef AES_H
#define AES_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// 🔹 Fix: Define AES_CONST_VAR (if not defined in your existing code)
#ifndef AES_CONST_VAR
#define AES_CONST_VAR const  // Use 'const' for read-only tables
#endif

// Function prototypes
void AES128_ECB_indp_setkey(uint8_t* key);
void AES128_ECB_indp_crypto(uint8_t* input);

#ifdef __cplusplus
}
#endif
#endif
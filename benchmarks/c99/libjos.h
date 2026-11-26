#ifndef LIBJOS_H
#define LIBJOS_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define LIBJOS_VERSION "0.1.0"
void jos_sha256_hex(const uint8_t *data, size_t len, char out_hex[65]);
int jos_seal_atom_buf(const char *name, const char *objective, char *out_json, size_t cap, char out_art[69]);
#ifdef __cplusplus
}
#endif
#endif

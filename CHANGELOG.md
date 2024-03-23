# Changelog

## 1.2.0
- Added CLI argument `--meter` to show graphical utilization meters.

## 1.1.0

- Added CLI argument `--id` to filter the processed GPUs (it is passed to `nvidia-smi`).
- Changed some error text to be printed to stderr instead of on stdout.
- The program now exits with the same error code as `nvidia-smi` if its call failed.

## 1.0.7

- Added CLI argument `--user` to filter processes by selected users.

## 1.0.6

- Fixed coloring output. Thanks @tomix1024 !

## 1.0.5

- Maintenance release.

## 1.0.4

- Fixed output when there are processed with PIDs >= 1M.

## 1.0.3

- Fixed outputting commands longer than 100 characters.

## 1.0.2

- No change, just re-release.

## 1.0.1

- Released on Jan 17 2021.
- Released on PyPi.

## 1.0

- Basic functionality, supports reading nvidia-smi from stdin, or calling it internally if not stdin is provided.

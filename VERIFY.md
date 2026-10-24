# Verifying the files

Three independent levels. Level 1 is enough to detect corruption; levels 2–3 prove the files come from
the author.

Signing key: **Vincent Liu &lt;elsevier2012@hotmail.com&gt;**
Fingerprint: `DA1A 1AEF D8B2 C17C FF3F 1D1B 3905 0F50 7A4F EC17`
The same fingerprint is published in the Zenodo record [10.5281/zenodo.23610035](https://doi.org/10.5281/zenodo.23610035) and on
[GitHub](https://github.com/AlienMuse.gpg) (`https://github.com/AlienMuse.gpg`).

## Level 1 — checksums

Download the PDFs and `SHA256SUMS` into one folder.

Linux / macOS:

```sh
sha256sum -c SHA256SUMS --ignore-missing
```

Windows PowerShell:

```powershell
Get-Content SHA256SUMS | ForEach-Object {
  $hash, $name = $_ -split '  ', 2
  if (Test-Path $name) {
    $ok = (Get-FileHash $name -Algorithm SHA256).Hash -eq $hash.ToUpper()
    "{0}  {1}" -f ($(if ($ok) { 'OK  ' } else { 'FAIL' })), $name
  }
}
```

## Level 2 — signature

```sh
gpg --import VincentLiu-signing-key.asc          # from this repository or the release
gpg --verify SHA256SUMS.asc SHA256SUMS
```

The output must say `Good signature from "Vincent Liu <elsevier2012@hotmail.com>"` and show the fingerprint
above.

## Level 3 — timestamps and platform attestation
GitHub releases of this repository are immutable and carry a GitHub-signed release attestation:

```sh
gh release verify v1.0.0 -R AlienMuse/strained-prismatic-geometry
gh release verify-asset v1.0.0 Strained-Prismatic-Geometry-v1.0.0-Complete.pdf -R AlienMuse/strained-prismatic-geometry
```

`SHA256SUMS.tsr` is an RFC 3161 timestamp token over `SHA256SUMS` from FreeTSA:

```sh
openssl ts -reply -in SHA256SUMS.tsr -text          # shows the time
openssl ts -verify -data SHA256SUMS -in SHA256SUMS.tsr \
    -CAfile timestamps/freetsa-cacert.pem -untrusted timestamps/freetsa-tsa.crt
```

A second, independent token over the same file comes from DigiCert. Its certificate chain up to the public
*DigiCert Trusted Root G4* is in `timestamps/digicert-chain.pem`; verify against your system's CA bundle:

```sh
openssl ts -verify -data SHA256SUMS -in timestamps/SHA256SUMS.digicert.tsr \
    -CAfile /etc/ssl/certs/ca-certificates.crt -untrusted timestamps/digicert-chain.pem
```

`SHA256SUMS.ots` anchors the same file in the Bitcoin blockchain (<https://opentimestamps.org>):

```sh
ots verify SHA256SUMS.ots
```

## Checksums of this release

```text
9234765e1c29373cf6d4c9206472c88a20374267136aeaa8bfec700e1ff53255  Strained-Prismatic-Geometry-v1.0.0-Complete.pdf
004de72794c58c381fdf993b196c465367fc55c747207898c06ec2ecc4fe570c  Strained-Prismatic-Geometry-v1.0.0-Preview.pdf
1de42b3ea1ac7b46185fa82f2a06b5e729019f780a89876f2aa28d15006aef0a  Strained-Prismatic-Geometry-v1.0.0-code.zip
```

# License Notice from SBOM Generator

## Overview
This project generates a license notice file using a CycloneDX-formatted Software Bill of Materials as its source.

While this tool endeavors to assist the complying with the requirements of publication of open source components,
it is limited by the accuracy of SBOMs and license information published by SPDX. The output files should be seen
as a starting point for creating notices and reviewed for accuracy before publication.

## Installation
To use this tool, you will need to clone the SPDX license list data repository into the same location as the tool.

    git clone https://github.com/spdx/license-list-data

You can also add custom licenses to the custom-license directory. Using it in conjunction with the override system,
you can add specific commercial licenses for dependencies that wouldn't normally appear in an SBOM.

### Overrides

If you have a ground truth you need to use to correct issues or augment information in SBOMs caused by the limitations
of scanning software, you can develop an override file to manually specify licenses for specific purls. There should
be one entry per line, formatted as follows.

    purl,add/replace/hide,identifier,"additional copyright information"

You can create your own identifiers to match custom files created in `custom-license-data`.

    * add: Include in the notices even if not in the sbom
    * replace: Only include in the noitces if in the sbom
    * hide: Hide from the notices file

## Running
Use the example SBOM to try the tool. Compare the output to the reference output.

    python3 convert_sbom_to_notices.py example_sbom.json

To apply an override file, optionally provide a third argument.

    python3 convert_sbom_to_notice.py example_sbom.json example_override.csv

## Contributing
Maintainers are accepting patches and contributions to this project.
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details about submitting contributions to this project.

## License
This project is licensed under the [Apache 2.0 License](LICENSE).

## Additional Resources
* https://cyclonedx.org/specification/overview/
* https://spdx.org/licenses/

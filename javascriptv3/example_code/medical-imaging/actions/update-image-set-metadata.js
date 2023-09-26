/*
* Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
* SPDX-License-Identifier: Apache-2.0
*/

import {fileURLToPath} from "url";

// snippet-start:[medical-imaging.JavaScript.datastore.updateImageSetMetadataV3]
import {UpdateImageSetMetadataCommand} from "@aws-sdk/client-medical-imaging";
import {MedicalImagingClient} from "../libs/medicalImagingClient.js";

/**
 * @param {string} datastoreID - The ID of the medical imaging data store.
 * @param {string} imageSetID - The ID of the medical imaging image set.
 * @param {string} latestVersionID - The ID of the medical imaging image set version.
 * @param {{}} updateMetadata - The metadata to update.
 *                            - Example metadata:
 *                                {
 *                                     DICOMUpdates: {
 *                                         updatableAttributes: "{
 *                                             \"SchemaVersion\": 1.1,
 *                                            \"Patient\": {
 *                                                \"DICOM\": {
 *                                                    \"PatientName\": \"Garcia^Gloria\"
 *                                                }
 *                                            }
 *                                        }"
 *                                    }
 *                                }
 */
export const updateImageSetMetadata = async (datastoreID = "xxxxxxxxxx",
                                             imageSetID = "xxxxxxxxxx",
                                             latestVersionID = "1",
                                             updateMetadata = {}) => {
    const response = await medicalImagingClient.send(
        new UpdateImageSetMetadataCommand({ datastoreID : datastoreID,
            imageSetID : imageSetID,
            latestVersionID : latestVersionID,
            updateMetadata : updateMetadata})
    );
    console.log(response);
    // {
    //     '$metadata': {
    //     httpStatusCode: 200,
    //         requestId: '6e81d191-d46b-4e48-a08a-cdcc7e11eb79',
    //         extendedRequestId: undefined,
    //         cfId: undefined,
    //         attempts: 1,
    //         totalRetryDelay: 0
    // },
    //     datastoreId: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    //     jobId: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    //     jobStatus: 'SUBMITTED',
    //     submittedAt: 2023-09-22T14:48:45.767Z
    // }
    return response;
};
// snippet-end:[medical-imaging.JavaScript.datastore.updateImageSetMetadataV3]

// Invoke main function if this file was run directly.
if (process.argv[1] === fileURLToPath(import.meta.url)) {
    await updateImageSetMetadata();
}


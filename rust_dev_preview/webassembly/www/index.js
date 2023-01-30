/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0.
 */

import init, { main } from "./pkg/aws_wasm.js";

export const initialize = async () => await init(); 

const countFunctions = async () => {
  const region = String(document.getElementById("region").value || "us-west-2");
  const verbose = document.getElementById("verbose").checked;
  document.getElementById("result").textContent = "";
  try {
    const result = await main(region, verbose);
    document.getElementById("result").textContent = result;
  } catch (err) {
    console.error(err);
  }
};

window.onload = initialize;
document.getElementById("run").addEventListener("click", countFunctions)

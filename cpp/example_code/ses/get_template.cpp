/*
   Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
   SPDX-License-Identifier: Apache-2.0
*/
/**
 * Before running this C++ code example, set up your development environment, including your credentials.
 *
 * For more information, see the following documentation topic:
 *
 * https://docs.aws.amazon.com/sdk-for-cpp/v1/developer-guide/getting-started.html
 *
 * For information on the structure of the code examples and how to build and run the examples, see
 * https://docs.aws.amazon.com/sdk-for-cpp/v1/developer-guide/getting-started-code-examples.html.
 *
 **/


#include <aws/core/Aws.h>
#include <aws/email/SESClient.h>
#include <aws/email/model/GetTemplateRequest.h>
#include <iostream>
#include "ses_samples.h"

// snippet-start:[cpp.example_code.ses.GetTemplate]
//! Get a template's attributes.
/*!
  \param templateName: The name for the template.
  \param clientConfiguration: AWS client configuration.
  \return bool: Function succeeded.
 */
bool AwsDoc::SES::getTemplate(const Aws::String &templateName,
                 const Aws::Client::ClientConfiguration &clientConfiguration)
{
    Aws::SES::SESClient sesClient(clientConfiguration);

    Aws::SES::Model::GetTemplateRequest getTemplateRequest;

    getTemplateRequest.SetTemplateName(templateName);

    Aws::SES::Model::GetTemplateOutcome outcome = sesClient.GetTemplate(getTemplateRequest);

    if (outcome.IsSuccess())
    {
        std::cout << "Successfully got template." << std::endl;
    }

    else
    {
        std::cerr << "Error getting template. " << outcome.GetError().GetMessage()
                  << std::endl;
    }

    return outcome.IsSuccess();
}

// snippet-end:[cpp.example_code.ses.GetTemplate]
/*
 *
 *  main function
 *
 *  Usage: 'Usage: Usage: run_get_template <template_name>'
 *
 *  Prerequisites: An existing SES template to retrieve.
 *
 */

#ifndef TESTING_BUILD

int main(int argc, char **argv)
{
  if (argc != 2)
  {
    std::cout << "Usage: run_get_template <template_name>";
    return 1;
  }
  Aws::SDKOptions options;
    options.loggingOptions.logLevel = Aws::Utils::Logging::LogLevel::Debug;
    Aws::InitAPI(options);
  {
    Aws::String template_name(argv[1]);

      Aws::Client::ClientConfiguration clientConfig;
      // Optional: Set to the AWS Region (overrides config file).
      // clientConfig.region = "us-east-1";

      AwsDoc::SES::getTemplate(template_name, clientConfig);
  }

  Aws::ShutdownAPI(options);
  return 0;
}

#endif // TESTING_BUILD

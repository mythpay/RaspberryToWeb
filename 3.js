const express = require("express");
const Stripe = require("stripe");
const axios = require("axios");
const app = express();
app.use(express.json());
const stripe = Stripe(
  "pk_live_51PsXX2RrQGH9YbSCLrjDs9TYucmJ2qiuWY7FhL3Lyn4Rz7O5RNKYynx9Rucgy0ffxPH24XIh4HbTU3GhOv7PTjOO002OMJ4817",
);

async function createPaymentMethod() {
  // 1. Create Customer
  //   const customer = await stripe.customers.create({
  //     name: "adan guerra",
  //     email: "strong.siman.light@gmail.com",
  //     address: {
  //       country: "US",
  //       postal_code: "78370",
  //     },
  //   });
  //   console.log("Customer ID:", customer.id);
  const paymentMethod = await stripe.paymentMethods.create({
    type: "card",
    card: {
      number: "4284711016115421",
      exp_month: "03",
      exp_year: "2027",
      cvc: "400",
    },
    billing_details: {
      name: "adan guerra",
      email: "strong.siman.light@gmail.com",
      address: {
        country: "US",
        postal_code: "78370",
      },
    },
  });

  console.log(paymentMethod);
  const paramspage = {
    eid: "NA",
    payment_method: paymentMethod.id,
    expected_amount: 500,
    last_displayed_line_item_group_details: {
      subtotal: 500,
      total_exclusive_tax: 0,
      total_inclusive_tax: 0,
      total_discount_amount: 0,
      shipping_rate_amount: 0,
    },
    expected_payment_method_type: "card",
    guid: "811be8bd-f8e1-4e07-abd6-9523bfcbd0928f7fa0",
    muid: "48e0f835-9e5d-44a0-bf5e-0fd3549e59751645f2",
    sid: "030fa585-124b-4036-8209-1018ee7bd5f5838f4c",
    key: "pk_live_51PsXX2RrQGH9YbSCLrjDs9TYucmJ2qiuWY7FhL3Lyn4Rz7O5RNKYynx9Rucgy0ffxPH24XIh4HbTU3GhOv7PTjOO002OMJ4817",
    version: "e27e2486c8",
    init_checksum: "lintSgHRFqLbeNNU7TcsPakdkZFtHGBo",
    js_checksum: "qto~d^n0=QU>azbu]]c&QcnQo>aPUY[Q$yave]Y;< ab<_d%o?U^`w",
    px3: "5065afee3df692c761d1ef94e081daf22984e9113ba8a0e08848f2a5189c6be5:4jlBEDy7wKlxe647xarFu6ja0UofgxwGLLMJGuMAUZn4UsKaB2TEvwiqu0c2Z6WCupE8yJiQlX83MowkPpD/Eg==:1000:2FJw5EnecJ4mpB5iM8pHmekx6OKslIsJyMP9ZXLtVaZRxVW9HP4HEMqIZ8SmpY0qhv4wNXe7bftrhnUOB+eSkccwJlZLlftcNDhF3YvgCdP/Y02/P/D5f74JT8Yx/7kRJSsqFDLUwE44n8M5A/46M70pRDCBruC6OA4hrOUVq/iN1/gSwjRIde9KhFo108ddGdoRfzlAhu+VqGxQe73GOjM+mwQ0K6tMU+05tz58V23NdR1HdtSr9uwbJsgb5o3k8lm4GbGjXUcvCc3Uu1mmaftOIJjXMbJrtnUnfsNtD67IsEIUose/tHOoM0U3rAjo411SqUmK4xjxY77a7gkwG32Az4pUZhL4TB0ro+pZ202TxYoT/zdNr+YssHAQAK/2MMUskey76Qtv+DNuTpeMzyhUQ7oi+olP5VIowKG8Zlfv1dwVxwtwDgm9cdtA7GhC1+0QoE9Pah9jmwwt8nJ4KsgKtgwE8VZB3/JctaBJi3wh3QA+T60mKeZU6IdBcaFhRVg3cZJXfcMqZw7+qv5r98VFrfbpuvk8duzr0O19yUY=",
    pxvid: "c4c3bf63-535f-11f1-8d58-18c193ada6e5",
    pxcts:
      "HtwmwOeevII7EFY3CTogqj4T70DH5bN/kSYVGZpKhHM=:lSbNjD0Qe8gyDiWDjsJE0Bxq-tc4RxSv76kBJH4X4XAzB4H5hUZTz65FDRPWXI/-q3WRCllhANefhSk3UPmEY6Dj9lFD/TehivPSwiM9RNWhaRsthCJ3R6DwFdiRW//O4KP940Y-Qh2J4RoGzkUy01iubF528rxLIVq-d6bRCPoak9CbWc72bHSUK79WroNf",
    passive_captcha_token:
      "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9....(truncated)",
    passive_captcha_ekey: "rv_timestamp",
    client_attribution_metadata: {
      client_session_id: "9189455a-63bd-489d-95bd-8eb8ae5a4d2d",
      checkout_session_id:
        "cs_live_a1fb87jBr9YU99DmsCtJAhOysL6AgvOA8z1ZVUM0Et7OohgUMDfx14nuIR",
      merchant_integration_source: "checkout",
      merchant_integration_version: "payment_link",
      payment_method_selection_flow: "automatic",
      checkout_config_id: "2b9c8808-9e4b-44cf-abe3-a53fde630813",
    },
    link_brand: "link",
  };
  const responsepage = await axios.post(
    `https://api.stripe.com/v1/payment_pages/cs_live_a1fb87jBr9YU99DmsCtJAhOysL6AgvOA8z1ZVUM0Et7OohgUMDfx14nuIR/confirm`,
    { params: paramspage },
    {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    },
  );

  console.log("payment_pages:", responsepage.data.payment_intent.id);
  const authparam = {
    source:
      responsepage.data.payment_intent.next_action.use_stripe_sdk
        .three_d_secure_2_source,
    browser: {
      fingerprintAttempted: false,
      fingerprintData: null,
      challengeWindowSize: null,
      threeDSCompInd: "Y",
      browserJavaEnabled: false,
      browserJavascriptEnabled: true,
      browserLanguage: "en-US",
      browserColorDepth: "32",
      browserScreenHeight: "864",
      browserScreenWidth: "1536",
      browserTZ: "300",
      browserUserAgent:
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    },
    one_click_authn_device_support: {
      hosted: false,
      same_origin_frame: false,
      spc_eligible: true,
      webauthn_eligible: true,
      publickey_credentials_get_allowed: true,
    },
    frontend_execution: "eyJmaW5nZXJwcmludE91dGNvbWUiOiJub3Rfc3VwcG9ydGVkIn0=",
    key: "pk_live_51PsXX2RrQGH9YbSCLrjDs9TYucmJ2qiuWY7FhL3Lyn4Rz7O5RNKYynx9Rucgy0ffxPH24XIh4HbTU3GhOv7PTjOO002OMJ4817",
  };
  //   const responseauth = await axios.post(
  //     `https://api.stripe.com/v1/3ds2/authenticate`,
  //     { params: authparam },
  //     {
  //       headers: {
  //         "Content-Type": "application/x-www-form-urlencoded",
  //       },
  //     },
  //   );
  //   console.log("responseauth:", responseauth.data);
  const response = await axios.get(
    `https://api.stripe.com/v1/payment_intents/${responsepage.data.payment_intent.id}`,
    {
      params: {
        is_stripe_sdk: false,
        client_secret: responsepage.data.payment_intent.client_secret,
        key: "pk_live_51PsXX2RrQGH9YbSCLrjDs9TYucmJ2qiuWY7FhL3Lyn4Rz7O5RNKYynx9Rucgy0ffxPH24XIh4HbTU3GhOv7PTjOO002OMJ4817",
      },
      headers: {
        Accept: "application/json",
      },
    },
  );
  console.log("PaymentIntent:", response.data);

  //   // 3. Attach Payment Method to Customer
  //   const attachedPaymentMethod = await stripe.paymentMethods.attach(
  //     paymentMethod.id,
  //     {
  //       customer: customer.id,
  //     },
  //   );

  //   console.log("Attached Payment Method:");
  //   console.log(attachedPaymentMethod);

  await new Promise((resolve) => setTimeout(resolve, 1000));
}

createPaymentMethod();

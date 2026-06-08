const axios = require("axios");
function formatFakeNumber(num) {
  // Creates fake test format: 590-00-0000
  const s = String(num).padStart(9, "0");

  return `${s.slice(0, 3)}-${s.slice(3, 5)}-${s.slice(5)}`;
}
async function testApi() {
  try {
    const payload = new URLSearchParams({
      "user[email]": "strong.siman.light@gmail.com",
      "user[password]": "delay",
      "account[first_name]": "Adan",
      "account[last_name]": "Guerra",
      payment_method: "credit_card",
      "credit_card[card_number]": "4284711016115421", // Stripe/Visa test card
      "credit_card[expiration_date(2i)]": "3",
      "credit_card[expiration_date(1i)]": "2027",
      "credit_card[verification_number]": "322",
      "address[zip]": "78370",
      layout: "fresh",
      "user[password]": "delay",
      "user[pwdelay]": true,
      "user[uid]": "7lOyeyBl4k",
      password: "delay",
      pwdelay: true,
      tos2: 1,
      "record_search[type]": "detailed_person_report",
      subscription_plan_name:
        "36_89_1_month_nofree_afill_freshness_limit_100_freepdf",
      "credit_card[tokenex_token]": "7FD2TBU1QGV874ZW7U4EPSI0FW37I5AYLV7XHY",
      tokenex_token: "7FD2TBU1QGV874ZW7U4EPSI0FW37I5AYLV7XHY",
      initialize_tokenex: true,
      seon_fraud_api_session:
        "W;6.10.0;WVziccYP3L9iSlMxEXRAGg==;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",
    });
    const headers = {
      accept: "*/*",
      "accept-language": "en-US,en;q=0.9",
      "content-type": "application/x-www-form-urlencoded",
      origin: "https://www.beenverified.com",
      referer:
        "https://www.beenverified.com/lp/32fc4f/5/subscribe?hide-fcra=true&direct_to_subscribe=true",
      "sec-ch-ua":
        '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": '"Windows"',
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-origin",
      "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",

      // optional cookies
      cookie:
        "gclid=CjwKCAjwwpDQBhAuEiwAa-4Wo4ueu_48Ubkle12ETsVXoUF6g-M-O4TyC1jZevOOfikbRPHhrkRj0RoC5TAQAvD_BwE; bv_sess=d54ae0ec-e31b-49eb-9c4e-028e2e68826c; bv_ref=https%3A%2F%2Fwww.google.com%2F; bv_ent=https://www.beenverified.com/?fn=Benjamin&utm_source=google&utm_medium=cpc&utm_campaign=BV_PPL_SEA_PRP_NAM_FNB_1_V2&utm_term=benjamin&utm_content=730453401550&matchtype=p&adgroup=179597893368&device=c&gad_source=1&gad_campaignid=22155780861&gbraid=0AAAAADrqa5kqG0XNCG9YFSMnjirsaX1NU&gclid=CjwKCAjwwpDQBhAuEiwAa-4Wo4ueu_48Ubkle12ETsVXoUF6g-M-O4TyC1jZevOOfikbRPHhrkRj0RoC5TAQAvD_BwE; bv_dat=1778687594.114; OptanonAlertBoxClosed=2026-05-13T15:53:29.025Z; _gcl_gs=2.1.k1$i1778687590$u33399725; OTGPPConsent=DBABLA~BVQqAAAAAAKA.QA; _bhp=f012b025-9d8a-473c-ac90-1b4c8da21d22; _ga=GA1.1.1645594824.1778687619; _scid=gBfWHP0tQKRFTK9Hj1Ggj44skpIsZsV9; _axwrt=0e2e9e35-489f-42d5-bc3d-2a0ddc69d914; IR_gbd=beenverified.com; _tt_enable_cookie=1; _ttp=01KRH0PFV5S9CSQV2DG1XGSQFW_.tt.1; IR_PI=2a9163b9-42d3-11f1-99cf-f739e263af1b%7C1778687622003; _sctr=1%7C1778648400000; _pin_unauth=dWlkPVlXWXpNVFUwWldRdFlUUTNPUzAwTldObExUZ3pORGN0WVRCbE5qYzRNVFZoTXpjeQ; axwrt=0e2e9e35-489f-42d5-bc3d-2a0ddc69d914; _gcl_aw=GCL.1778687669.CjwKCAjwwpDQBhAuEiwAa-4Wo4ueu_48Ubkle12ETsVXoUF6g-M-O4TyC1jZevOOfikbRPHhrkRj0RoC5TAQAvD_BwE; _hjSessionUser_25826=eyJpZCI6ImFlNDgzN2Y3LTc2MmEtNTA3Zi04NjJlLWQ4ZjY3ZTkxY2MyMyIsImNyZWF0ZWQiOjE3Nzg2ODc2MzA3NzQsImV4aXN0aW5nIjp0cnVlfQ==; __mmapiwsid=019e220c-0e2f-7e1c-95ad-c83799aed752:1f2263a58a15f95cc06aa9ba0267bdf2235d590e; wcabtmd=%7B%2243%22%3A80%7D; fabtmd=%7B%222218%22%3A%7B%22variation_group_id%22%3A2839%7D%2C%222237%22%3A%7B%22variation_group_id%22%3A2865%7D%2C%222212%22%3A%7B%22variation_group_id%22%3Anull%7D%7D; f3k2kqs7xc=366118e9ade26b05c0a8de41e1e96d57; tfpsi=3101772b-7657-432c-96a8-17dd24e15319; dicbo_id=%7B%22dicbo_fetch%22%3A1779179083714%7D; t-ip=1; _hjSession_25826=eyJpZCI6Ijk1Y2YwZDkwLWU3ZWMtNDQwNy1hNTk1LTViNjdjNzBiMGQ4ZiIsImMiOjE3NzkxNzkwODYyNjgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; flow_type=people; tatari-session-cookie=5d13ae05-4659-a288-9781-3f91e7a379a4; flw_dat=eyJmbG93X2NhdGVnb3J5IjoiZGlyZWN0LXRvLXNpZ251cCIsImZsb3dfdHlw%0AZSI6InBlb3BsZSIsImZsb3dfdWlkIjoiMzJmYzRmIiwicGFnZV9jYXRlZ29y%0AeSI6InN1YnNjcmliZSJ9%0A; bv_sup=https://www.beenverified.com/lp/32fc4f/5/subscribe?hide-fcra=true&direct_to_subscribe=true; _scid_r=kZfWHP0tQKRFTK9Hj1Ggj44skpIsZsV9Skm9xg; _rdt_uuid=1778687619511.0f26222f-a5c8-4322-8a43-a1114f30c8be; _uetsid=2ef80b50535c11f18a4ce7ed60bd50a8; _uetvid=e994d7904ee311f1a1b2b9b3af0524ad; IR_18103=1779179173933%7C0%7C1779179173933%7C%7C; OptanonConsent=isGpcEnabled=0&datestamp=Tue+May+19+2026+03%3A26%3A15+GMT-0500+(GMT-05%3A00)&version=202602.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=38add781-8a7d-48dc-8965-6cd6854ca210&interactionCount=1&isAnonUser=1&prevHadToken=0&landingPath=NotLandingPage&GPPCookiesCount=1&gppSid=7&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1&intType=1&geolocation=US%3BCA&AwaitingReconsent=false; tatari-cookie-test=38006564; ttcsid=1779179089309::O6ww6RkBhjTpRdJ3Muoj.3.1779179223825.0::1.82993.86597::134511.22.295.1946::133001.49.1589; ttcsid_CH19P2JC77UE8P0FFUUG=1779179089308::t7SPpLmFsBozV7n-KxLD.2.1779179223826.1; ax_visitor=%7B%22firstVisitTs%22%3A1778687621833%2C%22lastVisitTs%22%3A1778762974676%2C%22currentVisitStartTs%22%3A1779179082534%2C%22ts%22%3A1779179223831%2C%22visitCount%22%3A3%7D; _ga_LBVP7VLK40=GS2.1.s1779179077$o3$g1$t1779179223$j60$l0$h0; _gcl_au=1.1.305421832.1778687609.521944506.1779179139.1779179223; _beenverified3_session=tYV2wNFvi1xsrv8V2HDqIjRXYguaLd0SRj2OeQTs%2FG3ZoufPCPzvaVWEU8IAzmDHwWYbLX3ca4DGkRh9Q82mZjudx3vqw%2FYlse%2FsWR5ktKnFNoFB%2FIFJHCcOvAhgoFY2wKdrI4NsVYhXu4q3Nq9Fzy8%2B3tGx0sWWrrV%2Fbn%2Fm2CJHOLgDBnZMUfA%2F7Uz1Aqh347%2F6ERJokHqdzgXOi%2Fe1d1Sa674mjLWc5TPPgwW3Iqo8w1q7Pu8Pt2Om5EMBmW1VnxgtLtPGQVooQD9d1IQF7rPNeI6unpl5tnwsQX%2BrwCuI5iX69TFrJuZzYAh1FMWZIcz5Z9tBjxmkefVw4h71saSdBF%2BZqDWcui%2BzLDrL9Ku7nYG8QsPLpW%2B73ZcL7zWujupi%2Bgum%2FkqyrtV3XfkDNdxVYR9xgKTPwyzJk3lUovnDLs2syjQTKtU1z0YBL%2BYRq9Kux1SprRoFn6QC09sfR0YtDph0gr7fvvPN2a27bXnRl7aYi3lbF6WkNymo5KgMzCybv5NH3ma5%2BjZ%2BKcV1hF%2BcONfzYRYPS7B117IfktYmh1QuviFptzKTBerrQH%2BX8lbX9Mg%2B5GCDDyTRmFQQCD5I5f4a7A4NqpqDuOYQxwI4Mut8yN1uUPKwbUwgLdrSGfsJD6ugjRUUXtLO9R7mVMPnhJiGlZAzMsCCjJDcv7ZaEjRJrqhe07Ir6o8p0IxYjorWvthw0ALIajQ2GG72Hig%3D--XbUiss%2Br3rQUNAfk--zQFuLbl5elb8p8Ewcu1t0w%3D%3D; __cf_bm=lApdS5u3NfcJ95NDP8nBjzbrYeFpiERiOdv6R24tGTM-1779179216.717026-1.0.1.1-e61194NJViAadon1fQHgcbCJ3fQuUlszGGs4r3WvjEiLM5OjtkhatAu8rn.X_0kT_Alk8pp0u6zfc6ru3Lljk8c..HY9eXwsvGRoxCNWHqmO3tRc8XHa0Tkx_5mN40DH",
    };
    const response = await axios.post(
      "https://www.beenverified.com/api/v5/account.json",
      payload.toString(),
      {
        headers,
      },
    );

    console.log("Status:", response.status);
    console.log("Response:", response.data);
  } catch (err) {
    if (err.response) {
      console.log("Error Status:", err.response.status);
      console.log("Error Data:", err.response.data);
    } else {
      console.log(err.message);
    }
  }

  // Optional delay between requests
  await new Promise((resolve) => setTimeout(resolve, 1000));
}

testApi();

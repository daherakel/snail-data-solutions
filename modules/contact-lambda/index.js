// Example AWS Lambda handler (Node.js) to receive contact form submissions
// and send an email through Amazon SES. This is a minimal example for
// demonstration. Configure environment vars: SOURCE_EMAIL, DEST_EMAIL, AWS_REGION

const { SESClient, SendEmailCommand } = require("@aws-sdk/client-ses");

const region = process.env.AWS_REGION || "us-east-1";
const ses = new SESClient({ region });

exports.handler = async (event) => {
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    const { name, email, company, project } = body;

    if (!name || !email || !project) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "Missing required fields" }),
      };
    }

    const source = process.env.SOURCE_EMAIL; // e.g. no-reply@yourdomain.com (must be verified in SES)
    const to = process.env.DEST_EMAIL; // where to send contact notifications

    const messageBody = `New contact form submission:\n\nName: ${name}\nEmail: ${email}\nCompany: ${company || "-"}\n\nProject:\n${project}`;

    const params = {
      Destination: { ToAddresses: [to] },
      Message: {
        Body: { Text: { Data: messageBody } },
        Subject: { Data: `New contact from ${name}` },
      },
      Source: source,
      ReplyToAddresses: [email],
    };

    await ses.send(new SendEmailCommand(params));

    return {
      statusCode: 200,
      body: JSON.stringify({ ok: true }),
    };
  } catch (err) {
    console.error("Error sending contact email:", err);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message || "Internal error" }),
    };
  }
};

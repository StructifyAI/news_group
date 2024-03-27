use anyhow::Result;
use reqwest::header;
use serde::{Deserialize, Serialize};

use super::{r#trait::TextTrait, TextMessage};

const SMS_URL: &str = "https://api.sendblue.co/api/send-message";
const TYPING_INDICATOR: &str = "https://api.sendblue.co/api/send-typing-indicator";
const RECEIVED_MESSAGES: &str = "https://api.sendblue.co/accounts/messages";

#[derive(Debug, Default)]
pub struct SendBlueCommunications;

impl SendBlueCommunications {
    pub fn new() -> SendBlueCommunications {
        SendBlueCommunications {}
    }
}

#[async_trait::async_trait]
impl TextTrait for SendBlueCommunications {
    async fn send_message(&self, phone_number: &str, message: &str) -> Result<()> {
        #[derive(Serialize)]
        struct SendMessage {
            number: String,
            content: String,
        }

        // Create the client
        let client = reqwest::Client::new();

        // Define the payload using the struct
        let payload = SendMessage {
            number: phone_number.to_string(),
            content: message.to_string(),
        };

        // Create the request
        let res = client
            .post(SMS_URL)
            .header(header::CONTENT_TYPE, "application/json")
            .header(
                "sb-api-key-id",
                std::env::var("SB_API_KEY_ID").map_err(anyhow::Error::msg)?,
            )
            .header(
                "sb-api-secret-key",
                std::env::var("SB_API_SECRET_KEY").map_err(anyhow::Error::msg)?,
            )
            .json(&payload)
            .send()
            .await
            .map_err(anyhow::Error::msg)?;

        res.text().await.map_err(anyhow::Error::msg)?;

        Ok(())
    }

    async fn get_messages(&self, phone_number: &str, n: usize) -> Result<Vec<TextMessage>> {
        #[derive(Serialize)]
        struct SearchMessages {
            number: String,
            limit: usize,
        }

        // Create the client
        let client = reqwest::Client::new();

        // Create the request
        let res = client
            .get(RECEIVED_MESSAGES)
            .header(header::CONTENT_TYPE, "application/json")
            .header("sb-api-key-id", std::env::var("SB_API_KEY_ID")?)
            .header("sb-api-secret-key", std::env::var("SB_API_SECRET_KEY")?)
            .query(&SearchMessages {
                number: phone_number.to_string(),
                limit: n,
            })
            .send()
            .await
            .map_err(anyhow::Error::msg)?;

        if res.status() != 200 {
            return Err(anyhow::Error::msg(format!(
                "Received status code: {}",
                res.status()
            )));
        }

        #[derive(Deserialize)]
        pub(crate) struct Messages {
            messages: Vec<TextMessage>,
        }
        let text: Messages = res.json().await?;
        let mut filtered_messages = text
            .messages
            .into_iter()
            .filter(|m| m.number == phone_number)
            .collect::<Vec<_>>();
        // let messages: Messages = res.json().await?;

        // sort by most recent first
        filtered_messages.sort_by(|a, b| b.date.cmp(&a.date));

        Ok(filtered_messages.into_iter().take(n).collect())
    }

    async fn set_activity(&self, phone_number: &str) -> Result<()> {
        #[derive(Serialize)]
        struct TypingIndicator {
            number: String,
        }

        // Create the client
        let client = reqwest::Client::new();

        // Define the payload using the struct
        let payload = TypingIndicator {
            number: phone_number.to_string(),
        };

        // Create the request
        let res = client
            .post(TYPING_INDICATOR)
            .header(header::CONTENT_TYPE, "application/json")
            .header(
                "sb-api-key-id",
                std::env::var("SB_API_KEY_ID").map_err(anyhow::Error::msg)?,
            )
            .header(
                "sb-api-secret-key",
                std::env::var("SB_API_SECRET_KEY").map_err(anyhow::Error::msg)?,
            )
            .json(&payload)
            .send()
            .await
            .map_err(anyhow::Error::msg)?;

        let _body = res.text().await.map_err(anyhow::Error::msg)?;

        Ok(())
    }

    /// Clone boxed
    fn clone_box(&self) -> Box<dyn TextTrait> {
        Box::new(SendBlueCommunications::new())
    }
}

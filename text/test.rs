use anyhow::Result;

use crate::comms::Communication;

use super::{TextActivity, TextEnum, TextMessage, TextTrait};

#[derive(Debug)]
pub struct TestTexter {
    sendr: tokio::sync::mpsc::Sender<Communication>,
}

impl TestTexter {
    pub fn new(sendr: tokio::sync::mpsc::Sender<Communication>) -> TestTexter {
        TestTexter { sendr }
    }
}

#[async_trait::async_trait]
impl TextTrait for TestTexter {
    /// Send a text message to the end user.
    async fn send_message(&self, phone_number: &str, message: &str) -> Result<()> {
        self.sendr
            .send(Communication::Text(TextEnum::SendMessage(TextMessage {
                number: phone_number.to_string(),
                content: message.to_string(),
                is_outbound: true,
                date: chrono::Utc::now(),
            })))
            .await?;

        Ok(())
    }

    /// Get the last n messages
    async fn get_messages(&self, _phone_number: &str, _n: usize) -> Result<Vec<TextMessage>> {
        Ok(vec![])
    }

    /// Show that we are currently processing.
    async fn set_activity(&self, phone_number: &str) -> Result<()> {
        self.sendr
            .send(Communication::Text(TextEnum::SetActivity(TextActivity {
                number: phone_number.to_string(),
                set: true,
            })))
            .await?;

        Ok(())
    }

    /// Clone boxed
    fn clone_box(&self) -> Box<dyn TextTrait> {
        Box::new(TestTexter {
            sendr: self.sendr.clone(),
        })
    }
}

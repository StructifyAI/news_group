use anyhow::Result;

use logger::log::info;

use super::{TextMessage, TextTrait};

#[derive(Debug, Default)]
pub struct DummyTexter;

impl DummyTexter {
    pub fn new() -> DummyTexter {
        DummyTexter {}
    }
}

#[async_trait::async_trait]
impl TextTrait for DummyTexter {
    /// Send a text message to the end user.
    async fn send_message(&self, phone_number: &str, message: &str) -> Result<()> {
        info!("Sending message to {}: '{}'", phone_number, message);

        Ok(())
    }

    /// Get the last n messages
    async fn get_messages(&self, _phone_number: &str, _n: usize) -> Result<Vec<TextMessage>> {
        Ok(vec![])
    }

    /// Show that we are currently processing.
    async fn set_activity(&self, phone_number: &str) -> Result<()> {
        info!("Setting activity for {}", phone_number);

        Ok(())
    }

    /// Clone boxed
    fn clone_box(&self) -> Box<dyn TextTrait> {
        Box::new(DummyTexter::new())
    }
}

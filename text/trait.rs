use anyhow::Result;
use std::fmt::Debug;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug)]
pub enum TextEnum {
    SetActivity(TextActivity),
    SendMessage(TextMessage),
}

#[derive(Debug)]
pub struct TextActivity {
    pub number: String,
    pub set: bool,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TextMessage {
    pub number: String,
    pub content: String,
    pub is_outbound: bool,
    pub date: DateTime<Utc>,
    //  "date": "2023-08-15T16:04:38.866Z",
}

#[async_trait::async_trait]
pub trait TextTrait: Debug + Send + Sync {
    /// Send a text message to the end user.
    async fn send_message(&self, phone_number: &str, message: &str) -> Result<()>;

    /// Get the last n messages
    async fn get_messages(&self, phone_number: &str, n: usize) -> Result<Vec<TextMessage>>;

    /// Somehow show to the user that we are currently processing their request.
    /// This will be the three bubbles on iphones.
    async fn set_activity(&self, phone_number: &str) -> Result<()>;

    /// Clone boxed
    fn clone_box(&self) -> Box<dyn TextTrait>;
}

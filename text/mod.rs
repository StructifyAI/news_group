mod dummy;
mod sendblue;
mod test;
mod r#trait;

pub use sendblue::SendBlueCommunications;
pub use r#trait::{TextMessage, TextTrait, TextActivity, TextEnum};
pub use test::TestTexter;
pub use dummy::DummyTexter;

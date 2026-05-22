import {
    Client,
    GatewayIntentBits,
    SlashCommandBuilder,
    AttachmentBuilder
} from "discord.js";
import express from "express";
import dotenv from "dotenv";
import GIFEncoder from "gifencoder";
import { createCanvas, loadImage } from "canvas";

dotenv.config();

const client = new Client({
    intents: [GatewayIntentBits.Guilds]
});

client.once("ready", async () => {

    console.log(`${client.user.tag} でログイン`);

    const command = new SlashCommandBuilder()
        .setName("gif")
        .setDescription("画像をGIF化")
        .addAttachmentOption(option =>
            option
                .setName("image")
                .setDescription("画像")
                .setRequired(true)
        );

    await client.application.commands.create(command);

    console.log("/gif を登録しました");
});

client.on("interactionCreate", async interaction => {

    if (!interaction.isChatInputCommand()) return;
    if (interaction.commandName !== "gif") return;

    await interaction.deferReply();

    const attachment = interaction.options.getAttachment("image");

    if (!attachment) {
        await interaction.editReply("画像がありません");
        return;
    }

    try {

        const img = await loadImage(attachment.url);

        const width = img.width;
        const height = img.height;

        const encoder = new GIFEncoder(width, height);

        const chunks = [];

        encoder.createReadStream().on("data", chunk => {
            chunks.push(chunk);
        });

        encoder.start();
        encoder.setRepeat(0);
        encoder.setDelay(80);
        encoder.setQuality(10);

        const canvas = createCanvas(width, height);
        const ctx = canvas.getContext("2d");

        // 回転アニメ
        for (let angle = 0; angle < 360; angle += 20) {

            ctx.clearRect(0, 0, width, height);

            ctx.save();

            ctx.translate(width / 2, height / 2);
            ctx.rotate(angle * Math.PI / 180);

            ctx.drawImage(
                img,
                -width / 2,
                -height / 2,
                width,
                height
            );

            ctx.restore();

            encoder.addFrame(ctx);
        }

        encoder.finish();

        const buffer = Buffer.concat(chunks);

        const file = new AttachmentBuilder(buffer, {
            name: "output.gif"
        });

        await interaction.editReply({
            files: [file]
        });

    } catch (err) {

        console.error(err);

        await interaction.editReply("GIF生成失敗");
    }
});

const app = express();

const PORT = process.env.PORT || 8000;

app.get("/", (req, res) => {
    res.send("Bot is alive!");
});

app.listen(PORT, () => {
    console.log(`HTTP Server running on port ${PORT}`);
});

client.login(process.env.TOKEN);

const { Client, GatewayIntentBits, EmbedBuilder, ActivityType } = require('discord.js');
const client = new Client({ intents: [GatewayIntentBits.Guilds] });
const token = require('./config.json');
const fs = require('fs');

function is_track_init(user_id, speed, item, track) {
  if(bdd[user_id] != undefined && bdd[user_id][speed] != undefined && bdd[user_id][speed][item] != undefined && bdd[user_id][speed][item][track] != undefined){
    return true;
  }
  return false;
}

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
  setInterval(() => {
    client.user.setActivity(`${client.guilds.cache.size} servers`, { type: ActivityType.Watching })
}, 60000);
});

bdd = JSON.parse(fs.readFileSync('./bdd.json', 'utf8'));

const track_list = fs.readFileSync("./tracklist.txt", 'utf-8').split(/\r?\n/);

client.on('interactionCreate', async interaction => {
  if (!interaction.isChatInputCommand()) return;

  if (interaction.commandName === 'ping') {
    const embed = new EmbedBuilder().setTitle('Pong!').setColor(0x47e0ff).setDescription('took ' + client.ws.ping + 'ms');
    await interaction.reply({embeds: [embed], ephemeral: true});
  }
  if (interaction.commandName === 'select') {
    await interaction.reply({content: `selected ${interaction.options.get('colors').value} and ${interaction.options.get('numbers').value}`, ephemeral: true});
  }
  if (interaction.commandName === 'save_time') {
    const speed = interaction.options.get('speed').value;
    track = interaction.options.get('track').value;
    for (let i = 0; i < track_list.length; i++) {
        if (track_list[i].toLowerCase() == track.toLowerCase()) {
          track = track_list[i];
          break;
        }
        if (i == track_list.length - 1) {
          const embed = new EmbedBuilder().setTitle('Error').setColor(0xff0000).setDescription(`could not found \`${track}\` in the track list`);
          await interaction.reply({embeds: [embed], ephemeral: true});
          return;
        }
    }
    const time = interaction.options.get('time').value;
    const reg = new RegExp('^[0-9]:[0-5][0-9]\\.[0-9]{3}$');
    if (!reg.test(time)) {
      const embed = new EmbedBuilder().setTitle(`Invalid time format`).setColor(0xff0000).setDescription(`recived \`${time}\` please use this format instead -> \`1:23.456\``);
      await interaction.reply({embeds: [embed], ephemeral: true});
      return;
    }
    item = 'NI';
    if (interaction.options.get('item').value == 1) {
      item = 'Shroom';
    }
    if (is_track_init(interaction.user.id, speed, item, track)) {
      if (bdd[interaction.user.id][speed][item][track] < time) {
        const embed = new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`you already have \`${bdd[interaction.user.id][speed][item][track]}\` on this track`);
        await interaction.reply({embeds: [embed], ephemeral: true});
        return;
      }
      bdd[interaction.user.id][speed][item][track] = time;
    }
    if (bdd[interaction.user.id] == undefined) {
      bdd[interaction.user.id] = {
        "150": {
          "Shroom": {
          },
          "NI": {
          }
        },
        "200": {
          "Shroom": {
          },
          "NI": {
          }
        }
      };
    }
    bdd[interaction.user.id][speed][item][track] = time;
    fs.writeFile('./bdd.json', JSON.stringify(bdd, null, 4), (err) => {
      if (err) {
        interaction.reply({content: `error while saving the time`, ephemeral: true});
        return;
      }
    })
    const embed = new EmbedBuilder().setTitle(`Time saved`).setColor(0x47e0ff).setDescription(`saved **${time}** on \`${track}\`, ${speed}cc (${item})`);
    await interaction.reply({embeds: [embed]});``
  }
});

client.login(token.Quaxly);
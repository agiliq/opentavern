# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Member'
        db.delete_table(u'tavern_member')

        # Adding model 'Membership'
        db.create_table(u'tavern_membership', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tgroup_memberships', to=orm['auth.User'])),
            ('tavern_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='memberships', to=orm['tavern.TavernGroup'])),
            ('join_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'tavern', ['Membership'])

        # Adding unique constraint on 'Event', fields ['group', 'name']
        db.create_unique(u'tavern_event', ['group_id', 'name'])

        # Adding unique constraint on 'TavernGroup', fields ['name']
        db.create_unique(u'tavern_taverngroup', ['name'])


        # Changing field 'Attendee.member'
        db.alter_column(u'tavern_attendee', 'member_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tavern.Membership']))

    def backwards(self, orm):
        # Removing unique constraint on 'TavernGroup', fields ['name']
        db.delete_unique(u'tavern_taverngroup', ['name'])

        # Removing unique constraint on 'Event', fields ['group', 'name']
        db.delete_unique(u'tavern_event', ['group_id', 'name'])

        # Adding model 'Member'
        db.create_table(u'tavern_member', (
            ('join_date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tavern_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['tavern.TavernGroup'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tavern_groups', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'tavern', ['Member'])

        # Deleting model 'Membership'
        db.delete_table(u'tavern_membership')


        # Changing field 'Attendee.member'
        db.alter_column(u'tavern_attendee', 'member_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tavern.Member']))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'tavern.attendee': {
            'Meta': {'object_name': 'Attendee'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tavern.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tavern.Membership']"}),
            'rsvp_status': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'rsvped_on': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'tavern.event': {
            'Meta': {'unique_together': "(('group', 'name'),)", 'object_name': 'Event'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'ends_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tavern.TavernGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '250'}),
            'starts_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'tavern.membership': {
            'Meta': {'object_name': 'Membership'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'join_date': ('django.db.models.fields.DateTimeField', [], {}),
            'tavern_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships'", 'to': u"orm['tavern.TavernGroup']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tgroup_memberships'", 'to': u"orm['auth.User']"})
        },
        u'tavern.taverngroup': {
            'Meta': {'object_name': 'TavernGroup'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_groups'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'group_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'through': u"orm['tavern.Membership']", 'symmetrical': 'False'}),
            'members_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'organizers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'organizes_groups'", 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['tavern']